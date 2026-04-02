# Running unit tests
You can run tests either by using already created SC4S and Splunk instances, or you can use Docker Compose to create them instead. You can also mix these methods by providing, e.g., only Splunk and using Docker Compose to spin up an SC4S instance.

If you want to use an already existing SC4S and Splunk instance, you need to pass these arguments: `--sc4s_host=<SC4S_IP>`, `--sc4s_type=external` for SC4S and `--splunk_host=<HEC_ENDPOINT>`, `--splunk_type=external` for Splunk. If you want to use Docker Compose, you need to have it installed. You can review the Compose configuration at `tests/docker-compose.yml`.
 
Testing command for external setup:
```
poetry run pytest -v --tb=long \
--splunk_type=external \
--splunk_hec_token=<HEC_TOKEN> \
--splunk_host=<HEC_ENDPOINT> \
--sc4s_type=external \
--sc4s_host=<SC4S_IP> \
--splunk_user=<SPLUNK_USER>  \
--splunk_password=<SPLUNK_PASSWORD> \
--junitxml=test-results/test.xml \
-n <NUMBER_OF_JOBS> \
<TEST>
```

# Creating a unit test

To create a unit test, use the existing test case that is most similar to your use case. The naming convention for test files is `test_vendor_product.py`.

Below is a template for the unit test file:

```
# Copyright <current-year> Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("<addon-name>")
def test_<vendor_name>_<product_name>(
    record_property, setup_splunk, setup_sc4s, get_host_key
):
    host = get_host_key
    mt = env.from_string(
        "{{ mark }}{{ bsd }} {{ host }} <test-message>"
    )

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    message = mt.render(mark="<134>", bsd=bsd, host=host)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search _time={epoch} index=netfw host="{host}" sourcetype="<sourcetype>"'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
```

Before you put your raw log into the unit test, make sure that:

- The message is a valid Python string with escape characters placed correctly.
- Sensitive data has been redacted.

**Timestamps in tests**

When creating a unit test, pay close attention to time handling. You can use the `.timeutils` module to generate timestamps. The timestamp format you generate should match the original event format. In most cases, start by getting the current UTC time:

`dt = datetime.datetime.now(datetime.timezone.utc)`

Then use `time_operations`, which returns:

- `iso` — ISO 8601 / RFC 5424-style timestamp, e.g., `2026-03-09T15:04:05.123456+01:00`
- `bsd` — BSD syslog / RFC 3164-style timestamp (`%b %d %H:%M:%S`), e.g., `Mar 09 15:04:05`
- `time` — time of day with microseconds only (`%H:%M:%S.%f`), e.g., `15:04:05.123456`
- `date` — calendar date (`%Y-%m-%d`), e.g., `2026-03-09`
- `tzoffset` — timezone offset from local tz, e.g., `+0100`
- `tzname` — timezone name, e.g., `UTC`, `CET`, `PDT`
- `epoch` — epoch seconds plus microseconds as a string (`%s.%f`), e.g., `1741532645.123456`. It is usually trimmed with `[:-7]` for seconds only and `[:-3]` for milliseconds.

When creating a message template, make sure the format matches the original message. In some cases, the timestamp is not part of the header. For example, in this CEF message the timestamp is part of the `rt` field:

```
mt = env.from_string(
    "{{ mark }} CEF:0|A10|vThunder|4.1.4-GR1-P12|WAF|session-id|2|rt={{ bsd }} src=1.1.1.1 spt=34860 dst=1.1.1.1 dpt=80 dhost=test.host.local cs1=uiext_sec_waf cs2=1 act=learn cs3=learn app=HTTP requestMethod=GET cn1=0 request=/sales/ msg=New session created: Id\=1\n"
)
```
