from pydantic import BaseModel, Field

from app.schemas.base import ScheduleEveryMinute, VetExamination, TransactionType, DayOfWeek


class MilkConfigSchema(BaseModel):
    user_id: int
    schedule_every_minute: ScheduleEveryMinute | None = None
    enterprise_patterns: list[str] | None = None
    verified_products: list[str] | None = None
    verified_transaction_types: list[str] | None = None
    verified_vet_examinations: list[str] | None = None
    check_transport_number_format: bool = None
    days_of_week: list[int] = None
    start_hour: int | None = Field(ge=0, le=23, default=None)
    start_minute: int | None = Field(ge=0, le=59, default=None)
    end_hour: int | None = Field(ge=0, le=23, default=None)
    end_minute: int | None = Field(ge=0, le=59, default=None)


class DefaultMilkServiceConfigSchema(MilkConfigSchema):
    schedule_every_minute: int = ScheduleEveryMinute.five.value
    enterprise_patterns: list = []
    verified_products: list[str] = ["молоко сырое коровье", "молоко коровье сырое"]
    verified_transaction_types: list[str] = [TransactionType.chilled.value]
    verified_vet_examinations: list[str] = [VetExamination.vsefull.value]
    check_transport_number_format: bool = False
    days_of_week: list[int] = [day.value for day in DayOfWeek]
    start_hour: int = 0
    start_minute: int = 0
    end_hour: int = 23
    end_minute: int = 59


