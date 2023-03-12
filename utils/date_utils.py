import calendar
import datetime

DATE_FORMAT = '%Y%m%d'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def is_weekend(date):
    calendar_day = calendar.weekday(date.year, date.month, date.day)
    return calendar_day >= 5


def date2str(date, format=DATE_FORMAT):
    return date.strftime(format)


def str2date(str, format=DATE_FORMAT):
    return datetime.datetime.strptime(str, format)


def next_days(date, days=1):
    return date + datetime.timedelta(days=days)