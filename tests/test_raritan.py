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

# <110>M_00796:  User radware Session with client radware was terminated due to Inactivity.
@pytest.mark.addons("raritan")
def test_raritan_dsx(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{mark}}[Login Failed]: Authentication failed for user 'cartertest' from host '{{ key }}'\n"
    )
    message = mt.render(mark="<27>", key=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][9001])

    st = env.from_string('search index=infraops sourcetype=raritan:dsx "{{key}}"')
    search = st.render(epoch=epoch, key=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
