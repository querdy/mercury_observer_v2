import re
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timedelta
from typing import Any, Iterator

import pytz
from pydantic import BaseModel, field_validator, computed_field
from pydantic_core.core_schema import ValidationInfo

from app.schemas.milk_service import TransactionType, VetExamination, MilkConfigSchema
from app.settings import settings
from app.vetis.schemas.base import RequestSchema, RecipientInRequestSchema, ProductInRequestSchema, \
    TransactionAfterRequestSchema
from app.vetis.utils import date_str_to_datetime

_init_context_var = ContextVar('_init_context_var', default=None)


@contextmanager
def config_context(value: MilkConfigSchema) -> Iterator[None]:
    token = _init_context_var.set(value)
    try:
        yield
    finally:
        _init_context_var.reset(token)


class ValueWithIsValid(BaseModel):
    value: Any
    is_valid: bool


class DateWithIsValid(BaseModel):
    date_start: datetime | str | None
    date_end: datetime | None
    is_valid: bool


class MilkProductInRequestSchema(ProductInRequestSchema):
    def __init__(__pydantic_self__, **data: Any) -> None:
        __pydantic_self__.__pydantic_validator__.validate_python(
            data,
            self_instance=__pydantic_self__,
            context=_init_context_var.get(),
        )

    product_name: ValueWithIsValid
    volume: float
    unit: str
    date_from: DateWithIsValid
    date_to: DateWithIsValid
    purpose: ValueWithIsValid
    vet_examination: ValueWithIsValid
    text: str

    @computed_field
    @property
    def expiration(self) -> ValueWithIsValid:
        try:
            expire_1 = self.date_to.date_start - self.date_from.date_start
        except TypeError:
            expire_1 = None
        try:
            expire_2 = self.date_to.date_end - self.date_from.date_end
        except TypeError:
            expire_2 = None
        if expire_2 is None or expire_1 == expire_2:
            return ValueWithIsValid(
                value=expire_1,
                is_valid=expire_1 in settings.MILK_VALID_EXPIRATION or expire_1 is None
            )
        return ValueWithIsValid(value=(expire_1, expire_2), is_valid=False)

    @field_validator('date_from', mode='before')
    def v_date_from(cls, value: str) -> DateWithIsValid:
        dates = tuple(map(date_str_to_datetime, value.split(' - ')))
        if len(dates) == 1:
            return DateWithIsValid(
                date_start=dates[0],
                date_end=None,
                is_valid=dates[0] is not None and (datetime.now() - dates[0]).total_seconds() >= 0)
        elif len(dates) == 2:
            return DateWithIsValid(
                date_start=dates[0],
                date_end=dates[1],
                is_valid=all((dates[0] is not None and (datetime.now() - dates[0]).total_seconds() >= 0,
                              dates[1] is not None and (datetime.now() - dates[1]).total_seconds() >= 0)))
        else:
            return DateWithIsValid(date_start=None, date_end=None, is_valid=False)

    @field_validator('date_to', mode='before')
    def v_date_to(cls, value: str) -> DateWithIsValid:
        dates = tuple(map(date_str_to_datetime, value.split(' - ')))
        if len(dates) == 1:
            return DateWithIsValid(
                date_start=dates[0],
                date_end=None,
                is_valid=True)
        elif len(dates) == 2:
            return DateWithIsValid(
                date_start=dates[0],
                date_end=dates[1],
                is_valid=True)
        else:
            return DateWithIsValid(date_start=None, date_end=None, is_valid=False)

    @field_validator('vet_examination', mode='before')
    def v_vet_examination(cls, value: str, info: ValidationInfo) -> ValueWithIsValid:
        if VetExamination(value) in [VetExamination(vet_exam) for vet_exam in info.context.verified_vet_examinations]:
            return ValueWithIsValid(value=VetExamination(value), is_valid=True)
        return ValueWithIsValid(value=VetExamination(value), is_valid=False)

    @field_validator('purpose', mode='before')
    def v_purpose(cls, value: str) -> ValueWithIsValid:
        if value.lower() in settings.MILK_VALID_PURPOSE:
            return ValueWithIsValid(value=value, is_valid=True)
        return ValueWithIsValid(value=value, is_valid=False)

    @field_validator('product_name', mode='before')
    def v_product_name(cls, value: str, info: ValidationInfo) -> ValueWithIsValid:
        for product_name in info.context.verified_products:
            if product_name.lower() in value.lower():
                return ValueWithIsValid(value=value, is_valid=True)
        return ValueWithIsValid(value=value, is_valid=False)

    @field_validator('volume', mode='before')
    def is_digit(cls, value: str) -> float:
        return float(value)


class MilkRecipientInRequestSchema(RecipientInRequestSchema):
    recipient_enterprise: str
    recipient_company: str
    bill_of_lading: str
    bill_of_lading_date: ValueWithIsValid
    products: list[MilkProductInRequestSchema]

    @field_validator('bill_of_lading_date', mode='before')
    def v_bill_of_lading_date(cls, value: str) -> ValueWithIsValid:
        now_datetime = datetime.now(tz=pytz.timezone(settings.TZ)).replace(tzinfo=None)
        bill_of_lading_date = date_str_to_datetime(value)
        try:
            if now_datetime - bill_of_lading_date <= timedelta(days=2):
                return ValueWithIsValid(value=bill_of_lading_date, is_valid=True)
        except TypeError:
            pass
        return ValueWithIsValid(value=bill_of_lading_date, is_valid=False)


class MilkRequestSchema(RequestSchema):
    def __init__(__pydantic_self__, **data: Any) -> None:
        __pydantic_self__.__pydantic_validator__.validate_python(
            data,
            self_instance=__pydantic_self__,
            context=_init_context_var.get(),
        )

    number: str
    transaction_type: ValueWithIsValid
    auto_number: ValueWithIsValid
    recipients: list[MilkRecipientInRequestSchema]
    version: str
    accepted: bool = False
    confirmed: bool = False

    def is_valid(self) -> bool:
        attrs = [self.transaction_type, self.auto_number]
        for recipient in self.recipients:
            attrs.append(recipient.bill_of_lading_date)
            for product in recipient.products:
                attrs.append(product.product_name)
                attrs.append(product.date_from)
                attrs.append(product.expiration)
                attrs.append(product.purpose)
                attrs.append(product.vet_examination)
        return all(map(lambda x: x.is_valid, attrs))

    @field_validator('transaction_type', mode='before')
    def v_transaction_type(cls, value: str, info: ValidationInfo) -> ValueWithIsValid:
        if TransactionType(value) in [TransactionType(tr_type) for tr_type in info.context.verified_transaction_types]:
            return ValueWithIsValid(value=TransactionType(value), is_valid=True)
        return ValueWithIsValid(value=TransactionType(value), is_valid=False)

    @field_validator('auto_number', mode='before')
    def v_auto_number(cls, value: str, info: ValidationInfo) -> ValueWithIsValid:
        if info.context.check_transport_number_format:
            try:
                trailer_number = [number.strip() for number in value.split("/")][1]
                if re.match(settings.TRAILER_NUMBER_REGEX, trailer_number):
                    return ValueWithIsValid(value=value, is_valid=True)
                else:
                    return ValueWithIsValid(value=value, is_valid=False)
            except IndexError:
                return ValueWithIsValid(value=value, is_valid=True)
        else:
            return ValueWithIsValid(value=value, is_valid=True)
