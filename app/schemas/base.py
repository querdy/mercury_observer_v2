from enum import IntEnum, Enum

from pydantic import BaseModel


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


class PushSchema(BaseModel):
    user_id: int
    items: list[str | int]


class PullSchema(BaseModel):
    user_id: int
    item: str | int


class ReverseBooleanSchema(BaseModel):
    user_id: int
    field: str


class EnterpriseSchema(BaseModel):
    user_id: int
    enterprise_pattern: str
