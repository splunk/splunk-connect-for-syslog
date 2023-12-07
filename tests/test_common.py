# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import shortuuid
import pytz

from jinja2 import Environment, select_autoescape
from pytest import mark

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))


def test_defaultroute(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{ mark }} {{ bsd }} {{ host }} test something else\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix host="{{ host }}" sourcetype="nix:syslog" source="program:test"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


def test_defaultroute_port(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string("{{ mark }} {{ bsd }} {{ host }} porttest: something else\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][5514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="sc4s:simple:test_one"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


def test_fallback(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} testvp-{{ host }} test,test thist,thisdfsdf\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="testvp-{{ host }}" sourcetype="sc4s:fallback"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


def test_metrics(record_property,  setup_splunk, setup_sc4s):

    st = env.from_string(
        'mcatalog values(metric_name) WHERE metric_name="spl.sc4syslog.*" AND ("index"="*" OR "index"="_*") BY metric_name | fields metric_name'
    )
    search = st.render()

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)

    assert result_count != 0


def test_tz_guess(record_property,  setup_splunk, setup_sc4s):

    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, time, date, tzoffset, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} : %ASA-3-003164: TCP access denied by ACL from 179.236.133.160/3624 to outside:72.142.18.38/23\n"
    )
    message = mt.render(
        mark="<111>", bsd=bsd, host=host, date=date, time=time, tzoffset=tzoffset
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="cisco:asa" "%ASA-3-003164"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

def test_splunk_meta(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} {{ host }} sc4splugin: This test is for splunkmeta\n")
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string('search _time={{ epoch }} index=infraops host="{{ host }}" sourcetype="sc4s:local_example"')
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
    
def test_tz_fix_ny(record_property,  setup_splunk, setup_sc4s):

    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    # 10 minute offset (reserved for future use)
    #   dt = datetime.datetime.now(pytz.timezone('America/New_York')) - datetime.timedelta(minutes=10)

    dt = datetime.datetime.now(pytz.timezone("America/New_York")) - datetime.timedelta(
        minutes=15
    )
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} tzfny-{{ host }} sshd[123]: Timezone America/New_York\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix host="tzfny-{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


def test_tz_fix_ch(record_property,  setup_splunk, setup_sc4s):
    
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    # 10 minute offset (reserved for future use)
    #   dt = datetime.datetime.now(pytz.timezone('America/New_York')) - datetime.timedelta(minutes=10)

    dt = datetime.datetime.now(pytz.timezone("America/Chicago")) - datetime.timedelta(
        minutes=15
    )
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ mark }} {{ bsd }} tzfchi-{{ host }} sshd[123]: Timezone America/Chicago\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=osnix host="tzfchi-{{ host }}" sourcetype="nix:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1



def test_check_config_version(
    record_property,  setup_splunk, setup_sc4s
):

    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events:startup:err" "Configuration file format is too old" '
    )
    search = st.render()

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)

    assert result_count == 0


def test_check_config_version_multiple(
    record_property,  setup_splunk, setup_sc4s
):

    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events:startup:err" "you have multiple @version directives" '
    )
    search = st.render()

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)

    assert result_count == 0


# This test fails on circle; Cisco ACS single test seems to trigger a utf8 error.
# def test_check_utf8(record_property,  setup_splunk, setup_sc4s):
#     st = env.from_string(
#         'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events" "Input is valid utf8"'
#     )
#     search = st.render()

#     result_count, _ = splunk_single(setup_splunk, search)

#     record_property("resultCount", result_count)

#     assert result_count == 0


def test_check_sc4s_version(record_property,  setup_splunk, setup_sc4s):

    st = env.from_string(
        'search earliest=-50m@m latest=+1m@m index=main sourcetype="sc4s:events:startup:out" "sc4s version=" NOT "UNKNOWN"'
    )
    search = st.render()

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("resultCount", result_count)

    assert result_count == 1
