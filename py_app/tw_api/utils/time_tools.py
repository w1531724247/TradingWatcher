# 

import time
from datetime import datetime
from datetime import timedelta
from datetime import timezone

def getSecondTimestamp():
    ts = time.time()

    return int(ts);

def getMillisecondTimestamp():
    ts = time.time();

    return int(round(ts * 1000))

def getBeijingDate():
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )

    # 协调世界时
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    # debug(utc_now, utc_now.tzname())
    # debug(utc_now.date(), utc_now.tzname())

    # 北京时间
    beijing_now = utc_now.astimezone(SHA_TZ)
    # debug(beijing_now, beijing_now.tzname())
    # debug(beijing_now.date(), beijing_now.tzname())

    # 系统默认时区
    # local_now = utc_now.astimezone()
    # debug(local_now, local_now.tzname())
    # debug(local_now.date(), local_now.tzname())

    return beijing_now

def getBeijingDateString():
    beijing_now = getBeijingDate();

    date_str = "{0}-{1}-{2} {3}:{4}:{5}".format(str.zfill(str(beijing_now.year), 4),
                                                str.zfill(str(beijing_now.month), 2),
                                                str.zfill(str(beijing_now.day), 2),
                                                str.zfill(str(beijing_now.hour), 2),
                                                str.zfill(str(beijing_now.minute), 2),
                                                str.zfill(str(beijing_now.second), 2))
    return date_str

def getBeijingDateFromTimestamp(timestamp: int):
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )

    utc_time = datetime.utcfromtimestamp(timestamp)
    utc_time = utc_time.replace(tzinfo=timezone.utc)

    # 北京时间
    beijing_now = utc_time.astimezone(SHA_TZ)

    return beijing_now

def getUTCDateFromTimestamp(timestamp: int):
    utc_time = datetime.utcfromtimestamp(timestamp)
    utc_time = utc_time.replace(tzinfo=timezone.utc)

    return utc_time

def getBeijingDateFromMsTimestamp(ms_timestamp: int):

    return getBeijingDateFromTimestamp(ms_timestamp/1000);

def getBeijingDateStringFromTimestamp(timestamp: int):
    SHA_TZ = timezone(
        timedelta(hours=8),
        name='Asia/Shanghai',
    )

    utc_time = datetime.utcfromtimestamp(timestamp)
    utc_time = utc_time.replace(tzinfo=timezone.utc)

    # 北京时间
    beijing_now = utc_time.astimezone(SHA_TZ)

    return "{0}-{1}-{2} {3}:{4}:{5}".format(str(beijing_now.year).zfill(4), str(beijing_now.month).zfill(2), str(beijing_now.day).zfill(2), str(beijing_now.hour).zfill(2), str(beijing_now.minute).zfill(2), str(beijing_now.second).zfill(2));
