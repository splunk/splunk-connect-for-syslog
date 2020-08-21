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


def test_vectra_ai_hsc(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|hsc|Host Score Change|3|externalId=$host_id cat=$category dvc=$headend_addr dvchost=$dvchost shost=$host_name src=$host_ip dst=$host_ip flexNumber1Label=threat flexNumber1=$threat flexNumber2Label=certainty flexNumber2=$certainty cs4Label=Vectra Event URL cs4=$href start=$UTCTimeStartCEF end=$UTCTimeEndCEF cs1Label=sourceKeyAsset cs1=$src_key_asset cs2Label=destKeyAsset cs2=$dst_key_asset\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:hostscoring"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_asc(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|asc|Account Score Change|3|externalId=$account_id cat=$category dvc=$headend_addr flexNumber1Label=threat flexNumber1=$threat flexNumber2Label=certainty flexNumber2=$certainty cs1Label=Vectra Event URL cs1=$href start=$UTCTimeStartCEF end=$UTCTimeEndCEF\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountscoring"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_host_detect(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|$d_type|$d_type_vname|$severity|externalId=$detection_id cat=$category dvc=$headend_addr dvchost=$dvchost shost=$host_name src=$host_ip flexNumber1Label=threat flexNumber1=$threat flexNumber2Label=certainty flexNumber2=$certainty cs4Label=Vectra Event URL cs4=$href cs5Label=triaged cs5=$triaged dst=$dd_dst_ip dhost=$dd_dst_dns proto=$dd_proto dpt=$dd_dst_port out=$dd_bytes_sent in=$dd_bytes_rcvd start=$UTCTimeStartCEF end=$UTCTimeEndCEF\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:detect"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_accountdetect(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|$d_type|$d_type_vname|$severity|externalId=$detection_id cat=$category dvc=$headend_addr account=$accountflexNumber1Label=threat flexNumber1=$threat flexNumber2Label=certainty flexNumber2=$certainty cs4Label=Vectra Event URL cs4=$href cs5Label=triaged cs5=$triaged dst=$dd_dst_ip dhost=$dd_dst_dns dpt=$dd_dst_port out=$dd_bytes_sent in=$dd_bytes_rcvd start=$UTCTimeStartCEF end=$UTCTimeEndCEF\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountdetect"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_lockdown(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra Networks|X Series|$version|lockdown|Account Lockdown|3|externalId=$account_idcat=$categorydvc=$headend_addrsuser=$useraccount=$account_namecs1Label=action cs1=$actioncs2Label=success cs2=$successcs4Label=Vectra Event URL cs4=$hrefstart=$UTCTimeStartend=$UTCTimeEnd\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountlockdown"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_campaign(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|campaigns|$campaign_name|2| externalId=$campaign_id cat=CAMPAIGNS act=$action dvc=$headend_addr dvchost=$dvchost shost=$src_name src=$src_ip suid=$src_hid cs4Label=VectraEventURL cs4=$campaign_link dhost=$dest_name dst=$dest_ip  duid=$dest_id rt=$timestamp reason=$reason cs6Label=VectraDetectionIDcs6=$det_id\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:campaigns"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_audit(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|audit|user_action|0|dvc=$headend_addr dvchost=$dvchost suser=$user spriv=$role src=$source_ip deviceFacility=13 cat=user_action outcome=$result msg=$message\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:audit"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1


def test_vectra_ai_health(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} CEF:0|Vectra |X Series|$version|health|$type|0|dvc=$headend_addr dvchost=$dvchost deviceFacility=14 outcome=$result msg=$message\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:health"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
