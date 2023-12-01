from pydantic import BaseModel, model_validator

from app.schemas.milk_service import TransactionType, VetExamination


class EnterpriseMainPageSchema(BaseModel):
    number: str
    name: str
    input_documents_href: str = None
    input_documents_count: int = None
    request_href: str = None
    request_count: int = None

    @model_validator(mode='after')
    def check_pair(self):
        if (self.input_documents_href and self.input_documents_count is None
                or self.input_documents_count and self.input_documents_href is None
                or self.request_href and self.request_count is None
                or self.request_count and self.request_href is None):
            raise ValueError


class ProductInRequestSchema(BaseModel):
    product_name: str
    volume: str
    unit: str
    date_from: str
    date_to: str
    purpose: str
    vet_examination: VetExamination
    text: str


class RecipientInRequestSchema(BaseModel):
    recipient_enterprise: str
    recipient_company: str
    bill_of_lading: str
    bill_of_lading_date: str
    products: list[ProductInRequestSchema]


class RequestSchema(BaseModel):
    number: str
    transaction_type: TransactionType
    auto_number: str
    recipients: list[RecipientInRequestSchema]


class TransactionAfterRequestSchema(BaseModel):
    number: str
    version: str
    tuid: str
    waybill_id: str
