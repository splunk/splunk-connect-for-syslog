Below is an example for the unit test file:

```
# Copyright <current year> Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import pytest
import random
import pytz

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("a10networks")
def test_a10_vthunder(
    record_property, setup_splunk, setup_sc4s
):
    mt = env.from_string(
       "{{ mark }} CEF:0|A10|vThunder|4.1.4-GR1-P12|WAF|session-id|2|rt={{ bsd }} src=1.1.1.1 spt=34860 dst=1.1.1.1 dpt=80 dhost=test.host.local cs1=uiext_sec_waf cs2=1 act=learn cs3=learn app=HTTP requestMethod=GET cn1=0 request=/sales/ msg=New session created: Id\=1\n"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, _, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=dt.strftime("%b %d %Y %H:%M:%S"))

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netwaf sourcetype="a10networks:vThunder:cef" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

```

When creating a unit test, pay close attention to time handling. You can use the `.timeutils` module to generate timestamps. The timestamp format you generate should match the original event format. In most cases, start by getting the current UTC time:

`dt = datetime.datetime.now(datetime.timezone.utc)`

Then use `time_operations`, which returns:
- iso - ISO 8601 / RFC5424-style timestamp e.g. 2026-03-09T15:04:05.123456+01:00
- bsd - BSD syslog / RFC3164-style timestamp ("%b %d %H:%M:%S") e.g. Mar 09 15:04:05
- time - time of day with microseconds only ("%H:%M:%S.%f") e.g. 15:04:05.123456
- date - calendar date ("%Y-%m-%d") e.g. 2026-03-09
- tzoffset - timezone offset from local tz e.g. +0100
- tzname - timezone name e.g. UTC, CET, PDT
- epoch - epoch seconds plus microseconds as a string (`%s.%f`), for example `1741532645.123456`. It is usually trimmed with `[:-7]` for seconds only and `[:-3]` for milliseconds.

When creating a message template, make sure the format matches the original message itself. In some cases, the timestamp is not part of the header. For example, in this CEF message:

```
mt = env.from_string(
    "{{ mark }} CEF:0|A10|vThunder|4.1.4-GR1-P12|WAF|session-id|2|rt={{ bsd }} src=1.1.1.1 spt=34860 dst=1.1.1.1 dpt=80 dhost=test.host.local cs1=uiext_sec_waf cs2=1 act=learn cs3=learn app=HTTP requestMethod=GET cn1=0 request=/sales/ msg=New session created: Id\=1\n"
)
```

the timestamp is part of the `rt` field.

When creating tests for CEF messages, pay attention to the message format. There are two possibilities:
- Provided samples have pri marking, BSD date, and hostname. This means they use BSD syslog format as transport for CEF-formatted log messages. In this case, remember that the time in the search has to be truncated only to seconds precision. Also replace the time and hostname in the original log with the generated values, e.g.:
```
Dec 6 16:52:22 IP Dec 06 16:51:38 hostname CEF:0|JATP|Cortex|3.6.0.1444|email|Phishing|8|externalId=1504 ...
```
to
```
{{ bsd }} {{ host }} CEF:0|JATP|Cortex|3.6.0.1444|email|Phishing|8|externalId=1504 ...
```

- Provided samples don't have pri marking. In this case, the user samples should have an rt CEF field; if it's missing, don't create the test and explain the reason. Put the date into this field. Use the same format as the original message.
Always use the full event in the test; do not truncate it. If the user provides multiple events (fewer than 10), use all of them in the tests (parameterize the test).