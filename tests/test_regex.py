import re

from app.settings import settings


def test_trailer_number_regex():
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АА100159') is not None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АА100159RUS') is not None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АА100159 R U S') is not None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АА100159 RU S') is not None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АА100159 rus') is not None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АА10015 RU S') is None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'А100159 RU S') is None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АП100159 RU S') is None
    assert re.match(settings.TRAILER_NUMBER_REGEX, 'АП1001159 RUS') is None
