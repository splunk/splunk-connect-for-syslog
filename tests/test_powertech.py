# Copyright 2023 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("powertech")
def test_powertech(
    record_property, setup_splunk, setup_sc4s, get_host_key
):
    host = get_host_key
    mt = env.from_string(
       "{{ mark }}{{ bsd }} {{ host }} CEF:0|PowerTech|Interact|3.1|TCA0001|The bytestream file *N/*N /test/test/test/test/test/test.tmp authority has been changed for user profile TEST.|2|src=1.1.1.1 dst=0.0.0.0 msg=TYPE:JRN CLS:AUD JJOB:CYBAGENT JUSER:AGENTESP JNBR:898488 PGM:QLESPI OBJECT: LIBRARY: MEMBER: DETAIL:A *N *N *STMF AGENTESP  Y Y Y   Y Y Y Y   Y Y RPL        0000 00000 * * *NA /test/test/test/test/test/test.tmp"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=bsd, host=host)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netops sourcetype="PowerTech:Interact:cef" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1