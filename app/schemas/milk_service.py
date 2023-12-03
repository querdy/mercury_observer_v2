from enum import Enum, IntEnum

from pydantic import BaseModel, Field


class TransactionType(Enum):
    frozen = 'замороженные'
    chilled = 'охлажденные'
    cooled = 'охлаждаемые'
    ventilated = 'вентилируемые'


class ScheduleEveryMinute(IntEnum):
    one = 1
    five = 5
    ten = 10
    twenty = 20
    thirty = 30


class DayOfWeek(IntEnum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6

    def get_ru_value(self):
        days_of_week_ru = {
            'monday': 'Пн',
            'tuesday': 'Вт',
            'wednesday': 'Ср',
            'thursday': 'Чт',
            'friday': 'Пт',
            'saturday': 'Сб',
            'sunday': 'Вс'
        }
        return days_of_week_ru.get(self.name)


class VetExamination(Enum):
    unfulfilled = 'не подвергнута ветеринарно-санитарной экспертизе'
    vseraw = 'изготовлена из сырья, прошедшего ветеринарно-санитарную экспертизу'
    vsefull = 'подвергнута ветеринарно-санитарной экспертизе в полном объёме'


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
    verified_vet_examinations: list[str] = [item.value for item in VetExamination]
    check_transport_number_format: bool = False
    days_of_week: list[int] = [day.value for day in DayOfWeek]
    start_hour: int = 0
    start_minute: int = 0
    end_hour: int = 23
    end_minute: int = 59


class MilkPushSchema(BaseModel):
    user_id: int
    items: list[str | int]


class MilkPullSchema(BaseModel):
    user_id: int
    item: str | int


class MilkReverseBooleanSchema(BaseModel):
    user_id: int
    field: str


class MilkEnterpriseSchema(BaseModel):
    user_id: int
    enterprise_pattern: str
