# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("mcafee")
def test_data_mcafeewg(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]

    event = '{{mark}}{{ bsd }} {{ host }} {{ app }}: status="403/80" srcip="192.168.57.1" user="-" dhost="s3-eu-west-1.amazonaws.com" urlp="80" proto="HTTP/http" mtd="GET" urlc="Internet Services" rep="-31" mt="application/pdf" mlwr="BehavesLike.PDF.Exploit.vx" app="-" bytes="458/509/2813889/3001" ua="Chrome87-10.0" http_referrer="http://www.cpcheckme.com/" lat="0/0/165/2638" rule="Block If Virus Was Found" url="http://s3-eu-west-1.amazonaws.com/cp-chk-files/win7_64bit_big.pdf?static=CPCheckMe&rand=1608029225651" file_name="win7_64bit_big.pdf" destip="52.218.52.116" rep_level="Minimal Risk"'

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<30>", bsd=bsd, host=host, app="mwg")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netproxy _time={{ epoch }} sourcetype="mcafee:wg:kv" source="mcafee:wg" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = 'mwg: status=\\"403/80\\" srcip=\\"192.168.57.1\\" user=\\"-\\" dhost=\\"s3-eu-west-1.amazonaws.com\\" urlp=\\"80\\" proto=\\"HTTP/http\\" mtd=\\"GET\\" urlc=\\"Internet Services\\" rep=\\"-31\\" mt=\\"application/pdf\\" mlwr=\\"BehavesLike.PDF.Exploit.vx\\" app=\\"-\\" bytes=\\"458/509/2813889/3001\\" ua=\\"Chrome87-10.0\\" http_referrer=\\"http://www.cpcheckme.com/\\" lat=\\"0/0/165/2638\\" rule=\\"Block If Virus Was Found\\" url=\\"http://s3-eu-west-1.amazonaws.com/cp-chk-files/win7_64bit_big.pdf?static=CPCheckMe&rand=1608029225651\\" file_name=\\"win7_64bit_big.pdf\\" destip=\\"52.218.52.116\\" rep_level=\\"Minimal Risk\\"'

    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("mcafee")
def test_data_mcafeewg_product(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)
    # Tune time functions
    epoch = epoch[:-7]

    event = '{{mark}}{{ bsd }} {{ host }} {{ app }}: status="403/80" srcip="192.168.57.1" user="-" dhost="s3-eu-west-1.amazonaws.com" urlp="80" proto="HTTP/http" mtd="GET" urlc="Internet Services" rep="-31" mt="application/pdf" mlwr="BehavesLike.PDF.Exploit.vx" app="-" bytes="458/509/2813889/3001" ua="Chrome87-10.0" http_referrer="http://www.cpcheckme.com/" lat="0/0/165/2638" rule="Block If Virus Was Found" url="http://s3-eu-west-1.amazonaws.com/cp-chk-files/win7_64bit_big.pdf?static=CPCheckMe&rand=1608029225651" file_name="win7_64bit_big.pdf" destip="52.218.52.116" rep_level="Minimal Risk" ProductName="foo"'

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<30>", bsd=bsd, host=host, app="mwg")

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netproxy _time={{ epoch }} sourcetype="mcafee:wg:kv" source="mcafee:wg:foo" host="{{ host }}" _raw="{{ message }}"'
    )

    message1 = 'mwg: status=\\"403/80\\" srcip=\\"192.168.57.1\\" user=\\"-\\" dhost=\\"s3-eu-west-1.amazonaws.com\\" urlp=\\"80\\" proto=\\"HTTP/http\\" mtd=\\"GET\\" urlc=\\"Internet Services\\" rep=\\"-31\\" mt=\\"application/pdf\\" mlwr=\\"BehavesLike.PDF.Exploit.vx\\" app=\\"-\\" bytes=\\"458/509/2813889/3001\\" ua=\\"Chrome87-10.0\\" http_referrer=\\"http://www.cpcheckme.com/\\" lat=\\"0/0/165/2638\\" rule=\\"Block If Virus Was Found\\" url=\\"http://s3-eu-west-1.amazonaws.com/cp-chk-files/win7_64bit_big.pdf?static=CPCheckMe&rand=1608029225651\\" file_name=\\"win7_64bit_big.pdf\\" destip=\\"52.218.52.116\\" rep_level=\\"Minimal Risk\\" ProductName=\\"foo\\"'

    search = st.render(epoch=epoch, host=host, message=message1)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
