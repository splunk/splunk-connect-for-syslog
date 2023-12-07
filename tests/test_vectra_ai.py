# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import shortuuid
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <13>Aug 21 09:24:00 S180356X5A19242 vectra_cef -: CEF:0|Vectra Networks|X Series|5.8|hsc|Host Score Change|3|externalId=2765220 cat=HOST SCORING dvc=10.34.252.35 dvchost={{ host }} shost=snavpxdevdi2468.corp.firstam.com src=10.32.137.135 dst=10.32.137.135 flexNumber1Label=threat flexNumber1=22 flexNumber2Label=certainty flexNumber2=51 flexNumber3Label=privilege flexNumber3=1 cs3Label=scoreDecreases cs3=False cs4Label=Vectra Event URL cs4=https://10.34.252.35/hosts/2765220 start=1598027040563 end=1598027040563 cs1Label=sourceKeyAsset cs1=False cs2Label=destKeyAsset cs2=False

@pytest.mark.addons("vectra")
def test_vectra_ai_hsc(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef -: CEF:0|Vectra Networks|X Series|5.8|hsc|Host Score Change|3|externalId=2765220 cat=HOST SCORING dvc=10.111.111.35 dvchost={{ host }} shost=snavpxdevdi2468.corp.firstam.com src=10.111.11.135 dst=10.11.11.135 flexNumber1Label=threat flexNumber1=22 flexNumber2Label=certainty flexNumber2=51 flexNumber3Label=privilege flexNumber3=1 cs3Label=scoreDecreases cs3=False cs4Label=Vectra Event URL cs4=https://10.34.252.35/hosts/2765220 start={{ epoch }} end={{ epoch }} cs1Label=sourceKeyAsset cs1=False cs2Label=destKeyAsset cs2=False\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:hostscoring"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("vectra")
def test_vectra_ai_asc(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef -: CEF:0|Vectra Networks|X Series|$version|asc|Account Score Change|3|externalId=$account_id cat=$category dvc=$headend_addr flexNumber1Label=threat flexNumber1=$threat flexNumber2Label=certainty flexNumber2=$certainty cs1Label=Vectra Event URL cs1=$href start=$UTCTimeStartCEF end={{ epoch }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountscoring"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Aug 21 09:26:06 xxxxxxx vectra_cef -: CEF:0|Vectra Networks|X Series|5.8|smb_brute_force|SMB Brute-Force|7|externalId=110076 cat=LATERAL MOVEMENT dvc=10.34.11.35 dvchost={{ host }} shost=snavpfaxrfax001.corp.firstam.com src=172.17.111.111 flexNumber1Label=threat flexNumber1=70 flexNumber2Label=certainty flexNumber2=95 cs4Label=Vectra Event URL cs4=https://10.34.252.35/detections/110076?detail_id\=25428794 cs5Label=triaged cs5=False dst=172.17.111.111 dhost= proto= dpt=445 out=None in=None start=1570653042000 end=1598027100000
@pytest.mark.addons("vectra")
def test_vectra_ai_host_detect(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef -: CEF:0|Vectra Networks|X Series|5.8|smb_brute_force|SMB Brute-Force|7|externalId=110076 cat=LATERAL MOVEMENT dvc=10.34.11.35 dvchost={{ host }} shost=snavpfaxrfax001.corp.firstam.com src=172.17.111.111 flexNumber1Label=threat flexNumber1=70 flexNumber2Label=certainty flexNumber2=95 cs4Label=Vectra Event URL cs4=https://10.34.252.35/detections/110076?detail_id\=25428794 cs5Label=triaged cs5=False dst=172.17.111.111 dhost= proto= dpt=445 out=None in=None start=1570653042000 end={{ epoch }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:detect"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("vectra")
def test_vectra_ai_accountdetect(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef_account_detection -: CEF:0|Vectra Networks|X Series|$version|$d_type|$d_type_vname|$severity|externalId=$detection_id cat=$category dvc=$headend_addr account=$accountflexNumber1Label=threat flexNumber1=$threat flexNumber2Label=certainty flexNumber2=$certainty cs4Label=Vectra Event URL cs4=$href cs5Label=triaged cs5=$triaged dst=$dd_dst_ip dhost=$dd_dst_dns dpt=$dd_dst_port out=$dd_bytes_sent in=$dd_bytes_rcvd start=$UTCTimeStartCEF end={{ epoch }}\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountdetect"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("vectra")
def test_vectra_ai_lockdown(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef -: CEF:0|Vectra Networks|X Series|$version|lockdown|Account Lockdown|3|externalId=$account_idcat=$categorydvc=$headend_addrsuser=$useraccount=$account_namecs1Label=action cs1=$actioncs2Label=success cs2=$successcs4Label=Vectra Event URL cs4=$hrefstart=$UTCTimeStartend=$UTCTimeEnd\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountlockdown"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("vectra")
def test_vectra_ai_campaign(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef -: CEF:0|Vectra Networks|X Series|$version|campaigns|$campaign_name|2| externalId=$campaign_id cat=CAMPAIGNS act=$action dvc=$headend_addr dvchost={{ host }} shost=$src_name src=$src_ip suid=$src_hid cs4Label=VectraEventURL cs4=$campaign_link dhost=$dest_name dst=$dest_ip  duid=$dest_id rt=$timestamp reason=$reason cs6Label=VectraDetectionIDcs6=$det_id\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:campaigns"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("vectra")
def test_vectra_ai_audit(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} vectra_cef_audit -: CEF:0|Vectra Networks|X Series|5.8|audit|user_action|0|dvc=10.111.11.35 dvchost={{ host }} suser=anagarajan spriv=Security Analyst src=None deviceFacility=13 cat=user_action outcome=True msg=session timeout with length 8:07:13\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:audit"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


@pytest.mark.addons("vectra")
def test_vectra_ai_health(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} CEF:0|Vectra Networks|X Series|$version|health|$type|0|dvc=$headend_addr dvchost={{ host }} deviceFacility=14 outcome=$result msg=$message\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:health"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
