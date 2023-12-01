from datetime import datetime


def date_str_to_datetime(date: str) -> datetime:
    date_formats = ['%d.%m.%Y:%H', '%d.%m.%Y']
    for dateformat in date_formats:
        try:
            return datetime.strptime(date, dateformat)
        except ValueError:
            continue
