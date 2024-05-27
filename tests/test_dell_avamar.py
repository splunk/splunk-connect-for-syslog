# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))


test_cases = [
    '{{ mark }} {{ bsd }} {{ host }}: <Code> 22555 <Type> AUDIT <Severity> PROCESS <Category> SECURITY <User> email@my.com <HwSource> {{ host }} <Summary> Changed backup expiration. <path> /clients/Dev-Cert/Windows/test.com <createtime> 2024-02-03 02:32:09 CST <plugin> 3001 <labelnum> 388 <expiration> 2024-02-16 <requestor> <requestor domain="/" host="1.1.1.1" product="MCGUI" role="Administrator" user="email@my.com"/>',
]


@pytest.mark.parametrize("case", test_cases)
@pytest.mark.addons("dell")
def test_dell_avamar(
    record_property, setup_splunk, setup_sc4s, case
):
    host = 'amavar'

    dt = datetime.datetime.now()
    _, bsd, _, date, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(case + "\n")
    message = mt.render(mark="<141>", bsd=bsd, host=host, date=date)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="dell:avamar:msc" (host="{{ host }}" OR "{{ host }}")'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
