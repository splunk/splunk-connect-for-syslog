# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

@pytest.mark.addons("sophos")
def test_sophos_firewall_event(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    event = '{{ mark }} device="SFW" date=2022-04-25 time=15:27:08 timezone="CDT" device_name="XG430" device_id=C4203AY8GXPYJ21 log_id=010101600001 log_type="Firewall" log_component="Firewall Rule" log_subtype="Allowed" status="Allow" priority=Information duration=136 fw_rule_id=2 nat_rule_id=0 policy_type=1 user_name="{{ host }}" user_gp="" iap=15 ips_policy_id=1 appfilter_policy_id=0 application="MSN" application_risk=3 application_technology="Browser Based" application_category="General Internet" vlan_id="" ether_type=Unknown (0x0000) bridge_name="" bridge_display_name="" in_interface="Port1" in_display_interface="Port1" out_interface="" out_display_interface="" src_mac=00:56:2B:8B:10:70 dst_mac=00:EA:BD:05:39:BD src_ip=10.41.254.203 src_country_code=R1 dst_ip=205.39.17.23 dst_country_code=USA protocol="TCP" src_port=59932 dst_port=443 sent_pkts=18  recv_pkts=16 sent_bytes=2422 recv_bytes=9586 tran_src_ip= tran_src_port=0 tran_dst_ip=172.24.99.169 tran_dst_port=3128 srczonetype="LAN" srczone="LAN" dstzonetype="WAN" dstzone="WAN" dir_disp="" connevent="Stop" connid="2108879552" vconnid="" hb_health="No Heartbeat" message="" appresolvedby="Signature" app_is_cloud=0'

    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<30>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdlp sourcetype="sophos:xg:firewall" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("sophos")
def test_sophos_content_filtering_event(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    event = '{{ mark }}device="SFW" date=2022-04-25 time=15:27:08 timezone="CDT" device_name="XG430" device_id=C4207AY8QXPYJ2E log_id=050901616001 log_type="Content Filtering" log_component="HTTP" log_subtype="Allowed" status="" priority=Information fw_rule_id=2 user_name="{{ host }}" user_gp="" iap=15 category="Search Engines" category_type="Acceptable" url="https://www.google.com/" contenttype="" override_token="" httpresponsecode="" src_ip=10.1.24.13 dst_ip=216.239.38.120 protocol="TCP" src_port=58562 dst_port=443 sent_bytes=591 recv_bytes=4428 domain=www.google.com exceptions= activityname="" reason="" user_agent="" status_code="200" transactionid= referer="" download_file_name="" download_file_type="" upload_file_name="" upload_file_type="" con_id=2491244032 application="" app_is_cloud=0 override_name="" override_authorizer="" used_quota="0"'

    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<30>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netdlp sourcetype="sophos:xg:content_filtering" {{ host }}'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
