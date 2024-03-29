# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <182>Jan 19 10:47:33 host purity.test: INFO [root] This is a test message generated by Pure Storage FlashArray. UTC Time: 2022 Jan 19 15:47:33 Array Name: TTDSA-PS02
# <182>Oct  3 15:23:39 host /space_utility_json.py[98617]: {"payload": {"effective_used": 111111111111111, "total_extents": 111111111, "legacy_effective_used": 111111111111111, "legacy_total_extents": 111111111, "data_reduction": "1.111111111111111", "array_id": "1111111-111111111-111111111111111111", "version": "3.1", "product": "XX", "timestamp": "2023-10-03T19:23:37.924870+00:00"}, "signature": "XXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXX__XXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXX"}

test_data = [
        {
            "template": "{{mark}}{{ bsd }} {{ host }} purity.test: INFO [root] This is a test message generated by Pure Storage FlashArray. UTC Time: 2022 Jan 19 15:47:33 Array Name: TTDSA-PS02\n",
            "sourcetype": "purestorage:array:test"
        },
        {
            "template": '{{mark}}{{ bsd }} {{ host }} /space_utility_json.py[98617]: {"payload": {"effective_used": 111111111111111, "total_extents": 111111111, "legacy_effective_used": 111111111111111, "legacy_total_extents": 111111111, "data_reduction": "1.111111111111111", "array_id": "1111111-111111111-111111111111111111", "version": "3.1", "product": "XX", "timestamp": "2023-10-03T19:23:37.924870+00:00"}, "signature": "XXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXX__XXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXX_XXXXXXXXXXXXXXX"}',
            "sourcetype": "purestorage:array"
        }
]

@pytest.mark.parametrize("test_case", test_data)
@pytest.mark.addons("purestorage")
def test_pure_storage(record_property, setup_splunk, setup_sc4s, test_case):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(test_case["template"])
    message = mt.render(mark="<27>", bsd=bsd, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=infraops sourcetype={{sourcetype}} host="{{key}}"'
    )
    search = st.render(epoch=epoch, sourcetype=test_case["sourcetype"], key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
