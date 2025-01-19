import time
import ntplib
from datetime import datetime, timezone, timedelta
from time import ctime
import pytz

# for key, val in pytz.country_timezones.items():
#     print(key, '=', val, end=',')
system_time_delta = timedelta(hours=1) # you can update the timezone on here by updating number 1 to 2
sys_tz_obj = timezone(system_time_delta, name="SYSTIME")

def ntp_get_time():
    try:
        NIST = 'pool.ntp.org'
        ntp = ntplib.NTPClient()
        ntpResponse = ntp.request(NIST)                        
        today_dt = datetime.strptime(ctime(ntpResponse.tx_time), "%a %b %d %H:%M:%S %Y")
        return today_dt.astimezone(sys_tz_obj)
    except Exception as e:
        print("ntp_get_time: ", e)
        # today_dt = datetime.strptime(ctime(time.time()), "%a %b %d %H:%M:%S %Y")
        # return today_dt.astimezone(sys_tz_obj)
        return None

def ntp_get_time_from_string(time):
    try:
        date = datetime.strptime(time, "%d/%m/%Y %H:%M:%S")
        return date.astimezone(sys_tz_obj)
    except Exception as e:
        return ""

def ntp_get_time_from_object(date):
    return date.astimezone(sys_tz_obj)