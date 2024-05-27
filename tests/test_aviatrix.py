# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
import datetime

import pytest

env = Environment()


test_data = [
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudx_cli: AviatrixVPNSession: User=demo, Status=active, Gateway=demo, GatewayIP=52.52.76.149, VPNVirtualIP=192.168.0.6, PublicIP=N/A, Login=2016-08-17 22:07:38, Logout=N/A, Duration=N/A, RXbytes=N/A, TXbytes=N/A",
        "sourcetype": "aviatrix:cloudx-cli"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} kernel: [14167.983249] ***AviatrixUser***:IN= OUT=eth0 SRC=192.168.0.6 DST=68.67.154.85 LEN=64 TOS=0x00 PREC=0x00 TTL=63 ID=28916 DF PROTO=TCP SPT=50428 DPT=443 WINDOW=65535 RES=0x00 SYN URGP=0",
        "sourcetype": "aviatrix:kernel"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} kernel: [ 4976.320353] AvxRl gw1 D:IN=eth0 OUT=eth0 MAC=02:bd:e5:4f:d0:e2:02:d8:14:81:fc:48:08:00 SRC=10.240.1.60 DST=10.230.1.23 LEN=84 TOS=0x00 PREC=0x00 TTL=63 ID=45312 DF PROTO=ICMP TYPE=8 CODE=0 ID=2833 SEQ=1",
        "sourcetype": "aviatrix:kernel"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixLicsenseVPNUsers: users=2",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixTunnelStatusChange: src_gw=oregon-transit(AWS us-west-2) dst_gw=100.20.53.124(NA NA) old_state=Down new_state=Up",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixCMD: action=USERCONNECT_UPGRADE_TO_VERSION, argv=['--rtn_file', '/run/shm/rtn957594707', 'userconnect_upgrade_to_version', 'upgrade-status', ''], result=Success, reason=, username=admin",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixBGPOverlapCIDR: Time Detected: 2018-09-24 20:28:58.329881",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixGuardDuty: Account [aws], Region [us-east-1], Instance ID [i-0a675b03fafedd3f2], at 2018-09-23T02:05:35Z, 163.172.7.97 is performing SSH brute force attacks against i-0a675b03fafedd3f2.  Please tighten instance security group to avoid UnauthorizedAccess:EC2/SSHBruteForce threat",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixFireNet: Firewall i-021f23187b8ac81c9~~tran-fw-1 in FireNet VPC vpc-0f943cd05455358ac~~cal-transit-vpc-1 state has been changed to down.",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixVPNVersion:  The VPN connection was rejected as it did not satisfy the minimum version requirements. Current version: AVPNC-2.4.10 Required minimum version: AVPNC-2.5.7 . The rejected VPN user name is tf-aws-52-tcplb-user1",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixGatewayStatusChanged: status=down gwname=EMEA-ENG-VPNGateway",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} cloudxd: AviatrixBGPRouteLimitThreshold: This message is alerting you that the VGW listed below currently has 89 routes, which is approaching the VGW route limits (100). You can reduce the number of routes on VGW both from on-prem side and on Aviatrix Transit gateway by enabling Route Summarization feature.",
        "sourcetype": "aviatrix:cloudxd"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} /usr/local/bin/avx-gw-state-sync[1168]: 2022/05/25 15:57:43 AviatrixGwMicrosegPacket: POLICY=54ea65c4-313e-4b3d-8db3-1ecc4f0981db SRC_MAC=16:06:11:d7:a1:11 DST_MAC=16:54:ec:50:09:17 IP_SZ=84 SRC_IP=10.4.187.253 DST_IP=10.5.144.38 PROTO=ICMP SRC_PORT=0 DST_PORT=0 DATA=0x ACT=PERMIT ENFORCED=true",
        "sourcetype": "aviatrix:avx-gw-state-sync"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} perfmon.py: AviatrixGwNetStats: timestamp=2020-06-09T17:29:31.371791 name=test public_ip=10.23.183.116.fifo private_ip=172.31.78.160 interface=eth0 total_rx_rate=10.06Kb total_tx_rate=12.77Kb total_rx_tx_rate=2.85Kb total_rx_cum=207.16MB total_tx_cum=1.2MB total_rx_tx_cum=208.36",
        "sourcetype": "aviatrix:perfmon"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} perfmon.py: AviatrixGwSysStats: timestamp=2020-06-09T17:29:31.371791 name=test cpu_idle=68 memory_free=414640 memory_available=1222000 memory_total=1871644 disk_total=16197524 disk_free=10982084",
        "sourcetype": "aviatrix:perfmon"
    },
    {
        "event": "{{mark}} {{ timestamp }} {{ host }} avx-nfq: AviatrixFQDNRule2[CRIT]nfq_ssl_handle_client_hello() L#281  Gateway=spoke1-fqdn S_IP=172.32.1.144 D_IP=52.218.234.41 hostname=aviatrix-download.s3-us-west-2.amazonaws.com state=MATCHED  Rule=*.amazonaws.com;1",
        "sourcetype": "aviatrix:avx-nfq"
    }
]

@pytest.mark.addons("aviatrix")
@pytest.mark.parametrize("sample", test_data)
def test_aviatrix(
    record_property,  get_host_key, setup_splunk, setup_sc4s, sample
):
    host = get_host_key

    dt = datetime.datetime.now()
    formatted_date = dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z") + "+00:00"
    epoch = dt.astimezone().strftime("%s.%f")[:-3]

    mt = env.from_string(sample["event"] + "\n")
    message = mt.render(mark="<13>", timestamp=formatted_date, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype={{ sourcetype }} host={{ host }}'
    )
    search = st.render(epoch=epoch, sourcetype=sample["sourcetype"], host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("event", message)

    assert result_count == 1