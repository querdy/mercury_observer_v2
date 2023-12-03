from datetime import datetime


months = {
    'Январь': 'January',
    'Февраль': 'February',
    'Март': 'March',
    'Апрель': 'April',
    'Май': 'May',
    'Июнь': 'June',
    'Июль': 'July',
    'Август': 'August',
    'Сентябрь': 'September',
    'Октябрь': 'October',
    'Ноябрь': 'November',
    'Декабрь': 'December',
}


def date_str_to_datetime(date: str) -> datetime | None:
    date_formats = ['%d.%m.%Y:%H', '%d.%m.%Y', '%B %Y']
    for month_ru in months:
        if month_ru in date:
            date = date.replace(month_ru, months[month_ru])
    for dateformat in date_formats:
        try:
            return datetime.strptime(date, dateformat)
        except ValueError:
            continue


