import re
import datetime

# Helper functions
# Insert a character at given location in string (e.g space between ms and TZ offset 2020-02-12 12:46:39.323 -08:00)
def insert_char(string, char, integer):
    return string[0:integer] + char + string[integer:]

def removeZero(tz):
    return re.sub(r'\b0+(\d)(?=:)', r'\1', tz)

def time_operations(dt):
    # Generate an ISO 8601 (RFC 5424) compliant timestamp with local timezone offset (2020-02-12T12:46:39.323-08:00)
    # See https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    iso = dt.astimezone().isoformat(sep='T', timespec='microseconds')
    # Generate an BSD-style (RFC 3164) compliant timestamp with no timezone (Oct 25 13:08:00)
    bsd = dt.strftime("%b %d %H:%M:%S")

    # Other variants of timestamps needed for this log sample
    time = dt.strftime("%H:%M:%S.%f")
    date = dt.strftime("%Y-%m-%d")
    # Insert colon in tzoffset string; normally just 'tzoffset = dt.astimezone().strftime("%z")'
    # Could use helper function above; e.g. 'tzoffset = insert_char(dt.astimezone().strftime("%z"), ":", 3)'
    tzoffset = dt.astimezone().strftime("%z")
    tzname = dt.astimezone().strftime("%Z")

    # Derive epoch timestamp for use in search string
    # NOTE:  There are caveats with 'strftime("%s")', see references below

    # See https://stackoverflow.com/questions/11743019/convert-python-datetime-to-epoch-with-strftime
    # See https://docs.python.org/3/library/datetime.html#datetime-objects
    # Basically: Don't use 'utcnow()'

    # Strict way to get epoch as a string (rather than float) avoiding naive objects
    # epoch = dt.fromtimestamp(dt.timestamp()).strftime('%s')

    # Since datetime.now().astimezone() is aware, strftime() should be safe and form below OK
    # Trim last 3 or 7 characters of microsecond resolution to obtain milliseconds or whole seconds, respectively
    epoch = dt.astimezone().strftime("%s.%f")

    return iso, bsd, time, date, tzoffset, tzname, epoch
