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

# <134>1 2019-08-21T17:42:08.000z "sample_logs bluecoat[0]:SPLV5.1 c-ip=192.0.0.6 cs-bytes=6269 cs-categories="unavailable" cs-host=gg.hhh.iii.com cs-ip=192.0.0.6 cs-method=GET cs-uri-path=/Sample/abc-xyz-01.pqr_sample_Internal.crt/MFAwTqADAgEAMEcwRTBDMAkGBSsOAwIaBQAEFOoaVMtyzC9gObESY9g1eXf1VM8VBBTl1mBq2WFf4cYqBI6c08kr4S302gIKUCIZdgAAAAAnQA%3D%3D cs-uri-port=8000 cs-uri-scheme=http cs-User-Agent="ocspd/1.0.3" cs-username=user4 clientduration=0 rs-status=0 s-action=TCP_HIT s-ip=10.0.0.6 serveripservice.name="Explicit HTTP" service.group="Standard" s-supplier-ip=10.0.0.6 s-supplier-name=gg.hhh.iii.com sc-bytes=9469 sc-filter-result=OBSERVED sc-status=200 time-taken=20 x-bluecoat-appliance-name="10.0.0.6-sample_logs" x-bluecoat-appliance-primary-address=10.0.0.6 x-bluecoat-proxy-primary-address=10.0.0.6 x-bluecoat-transaction-uuid=35d24c931c0erecta-0003000012161a77e70-00042100041002145cc859ed c-url="http://randomserver:8000/en-US/app/examples/"
def test_bluecoatproxySG_kv(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }}Z {{host}} bluecoat[0]: SPLV5.1 c-ip=192.0.0.6 cs-bytes=6269 cs-categories=\"unavailable\" cs-host=gg.hhh.iii.com cs-ip=192.0.0.6 cs-method=GET cs-uri-path=/Sample/abc-xyz-01.pqr_sample_Internal.crt/MFAwTqADAgEAMEcwRTBDMAkGBSsOAwIaBQAEFOoaVMtyzC9gObESY9g1eXf1VM8VBBTl1mBq2WFf4cYqBI6c08kr4S302gIKUCIZdgAAAAAnQA%3D%3D cs-uri-port=8000 cs-uri-scheme=http cs-User-Agent=\"ocspd/1.0.3\" cs-username=user4 clientduration=0 rs-status=0 s-action=TCP_HIT s-ip=10.0.0.6 serveripservice.name=\"Explicit HTTP\" service.group=\"Standard\" s-supplier-ip=10.0.0.6 s-supplier-name=gg.hhh.iii.com sc-bytes=9469 sc-filter-result=OBSERVED sc-status=200 time-taken=20 x-bluecoat-appliance-name=\"10.0.0.6-sample_logs\" x-bluecoat-appliance-primary-address=10.0.0.6 x-bluecoat-proxy-primary-address=10.0.0.6 x-bluecoat-transaction-uuid=35d24c931c0erecta-0003000012161a77e70-00042100041002145cc859ed c-url=\"http://randomserver:8000/en-US/app/examples/\"")
    message = mt.render(mark="<134>", iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netproxy host=\"{{ host }}\" sourcetype=\"bluecoat:proxysg:access:kv\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
