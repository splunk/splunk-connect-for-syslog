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

def test_imperva_incapsula(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} " + 'CEF:0|Incapsula|SIEMintegration|1|1|Illegal Resource Access|3| fileid=3412341160002518171 sourceServiceName=site123.abcd.info siteid=1509732 suid=50005477 requestClientApplication=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0 deviceFacility=mia cs2=true cs2Label=Javascript Support cs3=true cs3Label=CO Support src=12.12.12.12 caIP=13.13.13.13 ccode=IL tag=www.elvis.com cn1=200 in=54 xff=44.44.44.44 cs1=NOT_SUPPORTED cs1Label=Cap Support cs4=c2e72124-0e8a-4dd8-b13b-3da246af3ab2 cs4Label=VID cs5=de3c633ac428e0678f3aac20cf7f239431e54cbb8a17e8302f53653923305e1835a9cd871db32aa4fc7b8a9463366cc4 cs5Label=clappsigdproc=Browser cs6=Firefox cs6Label=clapp ccode=IL cicode=Rehovot cs7=31.8969 cs7Label=latitude cs8=34.8186 cs8Label=longitude Customer=CEFcustomer123 ver=TLSv1.2 ECDHE-RSA-AES128-GCM-SHA256 start=1453290121336 request=site123.abcd.info/ requestmethod=GET qstr=p\=%2fetc%2fpasswd app=HTTP act=REQ_CHALLENGE_CAPTCHA deviceExternalID=33411452762204224 cpt=443 filetype=30037,1001, filepermission=2,1, cs9=Block Malicious User,High Risk Resources, cs9Label=Rule name' + "\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search _time={{ epoch }} index=netwaf host=\"{{ host }}\" sourcetype=\"cef\" source=\"Imperva:Incapsula\"")
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
