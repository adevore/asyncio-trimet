import re
import datetime

SUB_SECONDS_REGEXP = re.compile(r"\.\d{3}([-+])")
# Portland is located in UTC-8
TIMEZONE_OFFSET = -8
TIMEZONE = datetime.timezone(datetime.timedelta(hours=TIMEZONE_OFFSET))

def parse_trimet_time(timestamp):
    if isinstance(timestamp, str):
        timestamp = SUB_SECONDS_REGEXP.sub(r'\1', timestamp)
        return datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    elif isinstance(timestamp, int):
        seconds = timestamp // 1000
        return datetime.datetime.fromtimestamp(seconds, TIMEZONE)
    else:
        raise TypeError("Not a valid Trimet timestamp")