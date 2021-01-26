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


# <164>fenotify-1590500.warning: CEF:0|FireEye|CMS|9.0.1.923211|MC|malware-callback|7|requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0 cn2Label=sid cn2=11111112 cs5Label=cncHost cs5=172.65.203.203 spt=10400 smac=00:1c:7f:3f:a4:4a cn1Label=vlan cn1=0 cs4Label=link cs4=https://uswmsidccm1.cs.ball.com/event_stream/events_for_bot?ev_id\\=1590500 rt=Jan 25 2021 20:37:54 UTC proto=tcp dst=172.65.203.203 externalId=1590500 dmac=7c:ad:4f:10:06:83 dvchost=hrccnx01 cs6Label=channel cs6=GET /appliance-test/alert.html HTTP/1.1::~~Host: fedeploycheck.fireeye.com::~~User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0::~~Accept: text/html,application/xhtml+xml,application/xml;q\\=0.9,image/webp,*/*;q\\=0.8::~~Accept-Language: en-US,en;q\\=0.5::~~Accept-Encoding: gzip, deflate::~~DNT: 1::~~Connection: keep-alive::~~Cookie: _gcl_au\\=1.1.750220273.1606759464; _lfa\\=LF1.1.6e3cb721e7505c55.1606759467306; apt.uid\\=AP-VMCORKOEGG4K-2-1610403364179-83855235.0.2.bf309e5a-bdbb-4e90-be0b-3c182673fb8a; _uetvid\\=f6904ed04ea311eb9f93275a98a20e01::~~Upgrade-Insecure-Requests: 1::~~::~~ src=162.18.29.1 cn3Label=cncPort cn3=80 dpt=80 request=hxxp://fedeploycheck.fireeye.com/appliance-test/alert.html dvc=10.246.129.27 requestMethod=GET act=notified cs1Label=sname cs1=FETestEvent devicePayloadId=71de5c6d-5faa-4d60-b145-4d060f734023 start=Jan 25 2021 20:37:54 UTC ","PRI":"<164>","MESSAGE":"fenotify-1590500.warning: CEF:0|FireEye|CMS|9.0.1.923211|MC|malware-callback|7|requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0 cn2Label=sid cn2=11111112 cs5Label=cncHost cs5=172.65.203.203 spt=10400 smac=00:1c:7f:3f:a4:4a cn1Label=vlan cn1=0 cs4Label=link cs4=https://uswmsidccm1.cs.ball.com/event_stream/events_for_bot?ev_id\\=1590500 rt=Jan 25 2021 20:37:54 UTC proto=tcp dst=172.65.203.203 externalId=1590500 dmac=7c:ad:4f:10:06:83 dvchost=hrccnx01 cs6Label=channel cs6=GET /appliance-test/alert.html HTTP/1.1::~~Host: fedeploycheck.fireeye.com::~~User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0::~~Accept: text/html,application/xhtml+xml,application/xml;q\\=0.9,image/webp,*/*;q\\=0.8::~~Accept-Language: en-US,en;q\\=0.5::~~Accept-Encoding: gzip, deflate::~~DNT: 1::~~Connection: keep-alive::~~Cookie: _gcl_au\\=1.1.750220273.1606759464; _lfa\\=LF1.1.6e3cb721e7505c55.1606759467306; apt.uid\\=AP-VMCORKOEGG4K-2-1610403364179-83855235.0.2.bf309e5a-bdbb-4e90-be0b-3c182673fb8a; _uetvid\\=f6904ed04ea311eb9f93275a98a20e01::~~Upgrade-Insecure-Requests: 1::~~::~~ src=162.18.29.1 cn3Label=cncPort cn3=80 dpt=80 request=hxxp://fedeploycheck.fireeye.com/appliance-test/alert.html dvc=10.246.129.27 requestMethod=GET act=notified cs1Label=sname cs1=FETestEvent devicePayloadId=71de5c6d-5faa-4d60-b145-4d060f734023 start=Jan 25 2021 20:37:54 UTC
def test_fireeye_cms(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    # dt = datetime.datetime.now(datetime.timezone.utc)
    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }}fenotify-1590500.warning: CEF:0|FireEye|CMS|9.0.1.923211|MC|malware-callback|7|requestClientApplication=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0 cn2Label=sid cn2=11111112 cs5Label=cncHost cs5=172.65.203.203 spt=10400 smac=00:1c:7f:3f:a4:4a cn1Label=vlan cn1=0 cs4Label=link cs4=https://uswmsidccm1.cs.ball.com/event_stream/events_for_bot?ev_id\\=1590500 rt={{ bsd }} UTC proto=tcp dst=172.65.203.203 externalId=1590500 dmac=7c:ad:4f:10:06:83 dvchost={{ host }} cs6Label=channel cs6=GET /appliance-test/alert.html HTTP/1.1::~~Host: fedeploycheck.fireeye.com::~~User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0::~~Accept: text/html,application/xhtml+xml,application/xml;q\\=0.9,image/webp,*/*;q\\=0.8::~~Accept-Language: en-US,en;q\\=0.5::~~Accept-Encoding: gzip, deflate::~~DNT: 1::~~Connection: keep-alive::~~Cookie: _gcl_au\\=1.1.750220273.1606759464; _lfa\\=LF1.1.6e3cb721e7505c55.1606759467306; apt.uid\\=AP-VMCORKOEGG4K-2-1610403364179-83855235.0.2.bf309e5a-bdbb-4e90-be0b-3c182673fb8a; _uetvid\\=f6904ed04ea311eb9f93275a98a20e01::~~Upgrade-Insecure-Requests: 1::~~::~~ src=162.18.29.1 cn3Label=cncPort cn3=80 dpt=80 request=hxxp://fedeploycheck.fireeye.com/appliance-test/alert.html dvc=10.246.129.27 requestMethod=GET act=notified cs1Label=sname cs1=FETestEvent devicePayloadId=71de5c6d-5faa-4d60-b145-4d060f734023 start={{ bsd }} UTC\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netids host="{{ host }}" sourcetype="fe_cef_syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

