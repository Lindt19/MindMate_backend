#! /usr/bin/python3
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from datetime import date
import calendar


def getTime():
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    myTimeZone = " MEST"
    mm = str(now.month)
    dd = str(now.day)
    yyyy = str(now.year)
    hour = str(now.hour)
    minute = str(now.minute)
    if now.minute < 10:
        minute = '0' + str(now.minute)
    second = str(now.second)
    mydate = date.today()
    weekday = calendar.day_name[mydate.weekday()]
    return "It is  " + hour + ":" + minute + " o'clock"


def getDate():
    now = datetime.now(pytz.timezone("Europe/Berlin"))
    mm = str(now.month)
    dd = now.day
    yyyy = str(now.year)
    hour = str(now.hour)
    minute = str(now.minute)
    second = str(now.second)
    weekday = now.weekday()
    week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day = str(dd);
    if dd == 1:
        day += '.'
    else:
        day += '.'
    weekdayName = week[weekday]
    return "Today is  " + weekdayName + " of  " + day + mm + "." + yyyy


print("Hello!")
print(getTime())
print(getDate())
