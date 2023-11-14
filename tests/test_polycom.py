# Copyright 2019 Splunk, Inc.
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

polycom_data = [
    r"{{ mark }} {{ iso }}Z {{ host }} RPRM 107463 Jserver - DEBUG|||http-nio-5443-exec-22|com.polycom.rpum.epm.engine.ruleengine.ProfileFillingAction| ...df8-46f4-8ed1-2acc1bd62f97, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=call.autoOffHook.3.enabled, tagValue=1, required=true, canModify=true], ProfileTag [tagId=3e2fb279-c386-410b-866e-b427aaea80c4, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=call.teluri.showPrompt, tagValue=0, required=true, canModify=true], ProfileTag [tagId=6168b060-fe0e-414d-a25a-acbe629f963c, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=dialplan.3.applyToDirectoryDial, tagValue=1, required=true, canModify=true], ProfileTag [tagId=a835bbaf-1202-415a-8933-360a54acced1, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=dialplan.3.digitmap, tagValue=sip\:x.\.x.\@zoomcrc\.com|sip\:x.\@zoomcrc\.com|x.\.x.\@zoomcrc\.com|x.\@zoomcrc\.com|xxxxxxxxx.T|xxxxxxxxxx| , required=true, canModify=true], ProfileTag [tagId=67e41d5e-1112-4e36-8f78-e682ed61b4cc, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=dialplan.3.digitmap.timeOut, tagValue=4, required=true, canModify=true], ProfileTag [tagId=577dd248-7fdd-4730-aa90-ef7f1aa2f19b, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=dialplan.applyToDirectoryDial, tagValue=1, required=true, canModify=true], ProfileTag [tagId=f44bd920-fa45-4d11-90ff-2e294a45d1e1, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=dialplan.digitmap.lineSwitching.enable, tagValue=1, required=true, canModify=true], ProfileTag [tagId=5d1f9d8f-6583-4f5d-83c3-76194c299971, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=exchange.meeting.parseAllowedSipUriDomains, tagValue=zoomcrc.com,zoom.us,vip2.zoomus.com,bjn.vc,polycom.com, required=true, canModify=true], ProfileTag [tagId=b8a2dd79-7b8f-48be-b452-e529e2071003, profileUuid=47e0d340-5c83-4f6b-9692-9507cb6b3e83, tagName=exchange.meeting.parseEmailsAsSipUris, tagValue=1, required=true, canModify=true], ProfileTag [tagId=bfe8cd05...2048",
]


@pytest.mark.addons("polycom")
@pytest.mark.parametrize("event", polycom_data)
def test_polycom(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="polycom:rprm:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
