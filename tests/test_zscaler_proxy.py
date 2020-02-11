# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *

env = Environment(extensions=['jinja2_time.TimeExtension'])
#Note the long white space is a \t
#2019-10-16 15:44:36    reason=Allowed    event_id=6748427317914894361    protocol=HTTPS    action=Allowed    transactionsize=663    responsesize=65    requestsize=598    urlcategory=UK_ALLOW_Pharmacies    serverip=216.58.204.70    clienttranstime=0    requestmethod=CONNECT    refererURL=None    useragent=Windows Windows 10 Enterprise ZTunnel/1.0    product=NSS    location=UK_Wynyard_VPN->other    ClientIP=192.168.0.38    status=200    user=first.last@example.com    url=4171764.fls.doubleclick.net:443    vendor=Zscaler    hostname=4171764.fls.doubleclick.net    clientpublicIP=213.86.221.94    threatcategory=None    threatname=None    filetype=None    appname=DoubleClick    pagerisk=0    department=Procurement, Generics    urlsupercategory=User-defined    appclass=Sales and Marketing    dlpengine=None    urlclass=Bandwidth Loss    threatclass=None    dlpdictionaries=None    fileclass=None    bwthrottle=NO    servertranstime=0    md5=None
def test_zscaler_proxy(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{% now 'utc', '%Y-%m-%d %H:%M:%S' %}\treason=Allowed\tevent_id=6748427317914894361\tprotocol=HTTPS\taction=Allowed\ttransactionsize=663\tresponsesize=65\trequestsize=598\turlcategory=UK_ALLOW_Pharmacies\tserverip=216.58.204.70\tclienttranstime=0\trequestmethod=CONNECT\trefererURL=None\tuseragent=Windows Windows 10 Enterprise ZTunnel/1.0\tproduct=NSS\tlocation=UK_Wynyard_VPN->other\tClientIP=192.168.0.38\tstatus=200\tuser=first.last@example.com\turl=4171764.fls.doubleclick.net:443\tvendor=Zscaler\thostname={{host}}.fls.doubleclick.net\tclientpublicIP=213.86.221.94\tthreatcategory=None\tthreatname=None\tfiletype=None\tappname=DoubleClick\tpagerisk=0\tdepartment=Procurement, Generics\turlsupercategory=User-defined\tappclass=Sales and Marketing\tdlpengine=None\turlclass=Bandwidth Loss\tthreatclass=None\tdlpdictionaries=None\tfileclass=None\tbwthrottle=NO\tservertranstime=0\tmd5=None")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netproxy sourcetype=\"zscalernss-web\" hostname={{host}}.fls.doubleclick.net  | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
def test_zscaler_proxy_pri(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    mt = env.from_string(
        "{{mark}}{% now 'utc', '%Y-%m-%d %H:%M:%S' %}\treason=Allowed\tevent_id=6748427317914894362\tprotocol=HTTPS\taction=Allowed\ttransactionsize=663\tresponsesize=65\trequestsize=598\turlcategory=UK_ALLOW_Pharmacies\tserverip=216.58.204.70\tclienttranstime=0\trequestmethod=CONNECT\trefererURL=None\tuseragent=Windows Windows 10 Enterprise ZTunnel/1.0\tproduct=NSS\tlocation=UK_Wynyard_VPN->other\tClientIP=192.168.0.38\tstatus=200\tuser=first.last@example.com\turl=4171764.fls.doubleclick.net:443\tvendor=Zscaler\thostname={{host}}.fls.doubleclick.net\tclientpublicIP=213.86.221.94\tthreatcategory=None\tthreatname=None\tfiletype=None\tappname=DoubleClick\tpagerisk=0\tdepartment=Procurement, Generics\turlsupercategory=User-defined\tappclass=Sales and Marketing\tdlpengine=None\turlclass=Bandwidth Loss\tthreatclass=None\tdlpdictionaries=None\tfileclass=None\tbwthrottle=NO\tservertranstime=0\tmd5=None")
    message = mt.render(mark="<134>", host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search index=netproxy sourcetype=\"zscalernss-web\" hostname={{host}}.fls.doubleclick.net | head 2")
    search = st.render(host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
