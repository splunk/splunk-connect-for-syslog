# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()
# <3>2021-08-31T19:36:21Z tan-xxxx-xxx Tetration Alert[22745]: [ERR] {"keyId":"2c9515f3-0aed-3f84-b53b-7aba5bfdb859","eventTime":"1630438560000","alertTime":"1630438883933","alertText":"Live Analysis Annotated Flows contains escaped for \u003capplication_id:61157c97755f021c69cbe912\u003e","severity":"HIGH","tenantId":"0","type":"COMPLIANCE","alertDetails":"{\"consumer_scope_ids\":[\"5e435310497d4f28d4c4ce29\",\"5e94cb7a755f027feeb95f84\",\"5e94cbac755f027260b96026\",\"5e94cd3a497d4f4335c848e4\",\"5e94d253755f026c33b96004\",\"5ea1ecf4755f024b67b95fe7\"],\"consumer_scope_names\":[\"Default\",\"Default:UAL\",\"Default:UAL:A\",\"Default:UAL:A:PROD\",\"Default:UAL:A:PROD:2\",\"Default:UAL:A:PROD:2:ACU O365\"],\"provider_scope_names\":[\"Default\",\"Default:UAL\",\"Default:UAL:A\",\"Default:UAL:A:PROD\",\"Default:UAL:A:PROD:SHARED\"],\"provider_port\":31758,\"application_id\":\"61157c97755f021c69cbe912\",\"constituent_flows\":[{\"consumer_port\":32575,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.30\",\"provider_address\":\"10.0.0.0\",\"provider_port\":31758},{\"consumer_port\":24284,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.30\",\"provider_address\":\"10.0.0.0\",\"provider_port\":31758},{\"consumer_port\":24960,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.0\",\"provider_address\":\"10.0.0.29\",\"provider_port\":31758},{\"consumer_port\":32673,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.0\",\"provider_address\":\"10.0.0.29\",\"provider_port\":31758},{\"consumer_port\":32206,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.30\",\"provider_address\":\"10.0.0.29\",\"provider_port\":31758},{\"consumer_port\":23997,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.30\",\"provider_address\":\"10.0.0.29\",\"provider_port\":31758},{\"consumer_port\":24932,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.30\",\"provider_address\":\"10.0.0.0\",\"provider_port\":31758},{\"consumer_port\":26280,\"protocol\":\"TCP\",\"consumer_address\":\"10.0.0.0\",\"provider_address\":\"10.00.0.0\",\"provider_port\":31758}],\"escaped_count\":8,\"provider_scope_ids\":[\"5e435310497d4f28d4c4ce29\",\"5e94cb7a755f027feeb95f84\",\"5e94cbac755f027260b96026\",\"5e94cd3a497d4f4335c848e4\",\"5e94d253755f026c33b9600e\"],\"policy_type\":\"LIVE_POLICY\",\"protocol\":\"TCP\",\"internal_trigger\":{\"datasource\":\"live_analysis_compliance\",\"rules\":{\"field\":\"policy_violations\",\"type\":\"contains\",\"value\":\"escaped\"},\"label\":\"Alert Trigger\"},\"time_range\":[1630438560000,1630438679999],\"policy_category\":[\"ESCAPED\"]}","rootScopeId":"5e435310497d4f28d4c4ce29","alertConfId":"611d2e53dfad374757a558d3","alertTextWithNames":"Live Analysis Annotated Flows contains escaped for Live Analysis Application Root Alerting Scope - DO NOT ENFORCE!"}
def test_cisco_testration(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    #   Get UTC-based 'dt' time structure
    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    # iso from included timeutils is from local timezone; need to keep iso as UTC
    iso = dt.isoformat()[0:19]
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }} {{ iso }}Z {{ host }} Tetration Alert[22745]: [ERR] {"keyId":"2c9515f3-0aed-3f84-b53b-7aba5bfdb859","eventTime":"1630438560000","alertTime":"1630438883933","alertText":"Live Analysis Annotated Flows contains escaped for \\u003capplication_id:61157c97755f021c69cbe912\\u003e","severity":"HIGH","tenantId":"0","type":"COMPLIANCE","alertDetails":"{\\"consumer_scope_ids\\":[\\"5e435310497d4f28d4c4ce29\\",\\"5e94cb7a755f027feeb95f84\\",\\"5e94cbac755f027260b96026\\",\\"5e94cd3a497d4f4335c848e4\\",\\"5e94d253755f026c33b96004\\",\\"5ea1ecf4755f024b67b95fe7\\"],\\"consumer_scope_names\\":[\\"Default\\",\\"Default:UAL\\",\\"Default:UAL:A\\",\\"Default:UAL:A:PROD\\",\\"Default:UAL:A:PROD:2\\",\\"Default:UAL:A:PROD:2:ACU O365\\"],\\"provider_scope_names\\":[\\"Default\\",\\"Default:UAL\\",\\"Default:UAL:A\\",\\"Default:UAL:A:PROD\\",\\"Default:UAL:A:PROD:SHARED\\"],\\"provider_port\\":31758,\\"application_id\\":\\"61157c97755f021c69cbe912\\",\\"constituent_flows\\":[{\\"consumer_port\\":32575,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.30\\",\\"provider_address\\":\\"10.0.0.0\\",\\"provider_port\\":31758},{\\"consumer_port\\":24284,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.30\\",\\"provider_address\\":\\"10.0.0.0\\",\\"provider_port\\":31758},{\\"consumer_port\\":24960,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.0\\",\\"provider_address\\":\\"10.0.0.29\\",\\"provider_port\\":31758},{\\"consumer_port\\":32673,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.0\\",\\"provider_address\\":\\"10.0.0.29\\",\\"provider_port\\":31758},{\\"consumer_port\\":32206,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.30\\",\\"provider_address\\":\\"10.0.0.29\\",\\"provider_port\\":31758},{\\"consumer_port\\":23997,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.30\\",\\"provider_address\\":\\"10.0.0.29\\",\\"provider_port\\":31758},{\\"consumer_port\\":24932,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.30\\",\\"provider_address\\":\\"10.0.0.0\\",\\"provider_port\\":31758},{\\"consumer_port\\":26280,\\"protocol\\":\\"TCP\\",\\"consumer_address\\":\\"10.0.0.0\\",\\"provider_address\\":\\"10.00.0.0\\",\\"provider_port\\":31758}],\\"escaped_count\\":8,\\"provider_scope_ids\\":[\\"5e435310497d4f28d4c4ce29\\",\\"5e94cb7a755f027feeb95f84\\",\\"5e94cbac755f027260b96026\\",\\"5e94cd3a497d4f4335c848e4\\",\\"5e94d253755f026c33b9600e\\"],\\"policy_type\\":\\"LIVE_POLICY\\",\\"protocol\\":\\"TCP\\",\\"internal_trigger\\":{\\"datasource\\":\\"live_analysis_compliance\\",\\"rules\\":{\\"field\\":\\"policy_violations\\",\\"type\\":\\"contains\\",\\"value\\":\\"escaped\\"},\\"label\\":\\"Alert Trigger\\"},\\"time_range\\":[1630438560000,1630438679999],\\"policy_category\\":[\\"ESCAPED\\"]}","rootScopeId":"5e435310497d4f28d4c4ce29","alertConfId":"611d2e53dfad374757a558d3","alertTextWithNames":"Live Analysis Annotated Flows contains escaped for Live Analysis Application Root Alerting Scope - DO NOT ENFORCE!"}\n'
    )
    message = mt.render(mark="<166>", iso=iso, epoch=epoch, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="cisco:tetration"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
