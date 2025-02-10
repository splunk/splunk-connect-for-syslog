import shortuuid
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime

env = Environment(autoescape=select_autoescape(default_for_string=False))

# <13>Jan 16 11:51:35 xxxxxxx vectra_json_v2 -: {"version": "$version", "dvchost": "$dvchost", "host_ip": "$host_ip", "href": "$href", "src_key_asset": $src_key_asset, "host_id": $host_id, "headend_addr": "$headend_addr", "category": "HOST SCORING", "dst_key_asset": $dst_key_asset, "privilege": $privilege, "certainty": $certainty, "score_decreases": $score_decreases, "vectra_timestamp": "$timestamp", "host_name": "$host_name", "threat": $threat}

@pytest.mark.addons("vectra")
def test_vectra_ai_hostscoring_json(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_v2 -: {"version": "$version", "dvchost": "$dvchost", "host_ip": "$host_ip", "href": "$href", "src_key_asset": $src_key_asset, "host_id": $host_id, "headend_addr": "$headend_addr", "category": "HOST SCORING", "dst_key_asset": $dst_key_asset, "privilege": $privilege, "certainty": $certainty, "score_decreases": $score_decreases, "vectra_timestamp": "$timestamp", "host_name": "$host_name", "threat": $threat}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:hostscoring:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_account_v2 -: {"category": "ACCOUNT SCORING", "account_id": $account_id, "href": "$href", "certainty": $certainty, "privilege": $privilege, "score_decreases": $score_decreases, "version": "$version", "vectra_timestamp": "$timestamp", "headend_addr": "$headend_addr", "threat": $threat, "account_uid": "$account_uid"}
@pytest.mark.addons("vectra")
def test_vectra_ai_accountscoring_json(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_account_v2 -: {"category": "ACCOUNT SCORING", "account_id": $account_id, "href": "$href", "certainty": $certainty, "privilege": $privilege, "score_decreases": $score_decreases, "version": "$version", "vectra_timestamp": "$timestamp", "headend_addr": "$headend_addr", "threat": $threat, "account_uid": "$account_uid"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountscoring:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_v2 -: {"d_type_vname": "$d_type_vname", "dvchost": "$dvchost", "host_ip": "$host_ip", "href": "$href", "detection_id": $detection_id, "dd_bytes_sent": $dd_bytes_sent, "headend_addr": "$headend_addr", "dd_dst_port": $dd_dst_port, "category": "$category", "dd_bytes_rcvd": $dd_bytes_rcvd, "dd_dst_dns": "$dd_dst_dns", "severity": $severity, "certainty": $certainty, "triaged": $triaged, "vectra_timestamp": "$timestamp", "version": "$version", "host_name": "$host_name", "threat": $threat, "dd_dst_ip": "$dd_dst_ip", "dd_proto": "$dd_proto", "d_type": "$d_type"}
@pytest.mark.addons("vectra")
def test_vectra_ai_hostdetect_json(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_v2 -: {"d_type_vname": "$d_type_vname", "dvchost": "$dvchost", "host_ip": "$host_ip", "href": "$href", "detection_id": $detection_id, "dd_bytes_sent": $dd_bytes_sent, "headend_addr": "$headend_addr", "dd_dst_port": $dd_dst_port, "category": "$category", "dd_bytes_rcvd": $dd_bytes_rcvd, "dd_dst_dns": "$dd_dst_dns", "severity": $severity, "certainty": $certainty, "triaged": $triaged, "vectra_timestamp": "$timestamp", "version": "$version", "host_name": "$host_name", "threat": $threat, "dd_dst_ip": "$dd_dst_ip", "dd_proto": "$dd_proto", "d_type": "$d_type"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:hostdetect:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_account_v2 -: {"d_type_vname": "$d_type_vname", "dvchost": "$dvchost", "href": "$href", "detection_id": $detect ion_id, "dd_bytes_sent": $dd_bytes_sent, "headend_addr": "$headend_addr", "dd_dst_port": $dd_dst_ port, "category": "$category", "dd_bytes_rcvd": $dd_bytes_rcvd, "dd_dst_dns": "$dd_dst_dns", "sev erity": $severity, "certainty": $certainty, "triaged": $triaged, "vectra_timestamp": "$timestamp", "account_uid": "$account_uid", "version": "$version", "threat": $threat, "dd_dst_ip": "$dd_dst_ip", "d_type": "$d_type"}
@pytest.mark.addons("vectra")
def test_vectra_ai_accountdetect_json(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_account_v2 -: {"d_type_vname": "$d_type_vname", "dvchost": "$dvchost", "href": "$href", "detection_id": $detect ion_id, "dd_bytes_sent": $dd_bytes_sent, "headend_addr": "$headend_addr", "dd_dst_port": $dd_dst_ port, "category": "$category", "dd_bytes_rcvd": $dd_bytes_rcvd, "dd_dst_dns": "$dd_dst_dns", "sev erity": $severity, "certainty": $certainty, "triaged": $triaged, "vectra_timestamp": "$timestamp", "account_uid": "$account_uid", "version": "$version", "threat": $threat, "dd_dst_ip": "$dd_dst_ip", "d_type": "$d_type"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountdetect:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_v2 -: {"category": "$category ", "version": "$version", "success": "$success", "vectra_timestamp": "$UTCTime", "will_retry": "$retry", "href": "$href", "host_name": "$host_name", "action": "$action", "host_id": "$host_id", "headend_addr": "$headend_addr", "user": "$user"}
@pytest.mark.addons("vectra")
def test_vectra_ai_hostlockdown_json(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_v2 -: {"category": "$category ", "version": "$version", "success": "$success", "vectra_timestamp": "$UTCTime", "will_retry": "$retry", "href": "$href", "host_name": "$host_name", "action": "$action", "host_id": "$host_id", "headend_addr": "$headend_addr", "user": "$user"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:hostlockdown:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_account_v2 -: {"category": "$category", "account_id": $account_id, "success": $success, "href": "$href", "vectra_timestamp": "$UTCTime", "headend_addr": "$headend_addr", "user": "$user", "version": "$version", "action": "$action", "account_uid": "$account_name"}
@pytest.mark.addons("vectra")
def test_vectra_ai_accountlockdown_json(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_account_v2 -: {"category": "$category", "account_id": $account_id, "success": $success, "href": "$href", "vectra_timestamp": "$UTCTime", "headend_addr": "$headend_addr", "user": "$user", "version": "$version", "action": "$action", "account_uid": "$account_name"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:accountlockdown:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_v2 -: {"src_hid": "$src_hid", "timestamp": "$syslog_timestamp", "dvchost": "$dvchost", "campaign_id": "$campaign_id", "reason": "$reason", "src_name": "$src_name", "campaign_name": "$campaign_name", "campaign_link": "$campaign_link", "headend_addr": "$headend_addr", "dest_name": "$dest_name", "dest_id": "$dest_id", "vectra_timestamp": "$vectra_timestamp", "src_ip": "$src_ip", "version": "$version", "action": "$action", "dest_ip": "$dest_ip", "det_id": "$det_id"}
@pytest.mark.addons("vectra")
def test_vectra_ai_campaign_json(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_v2 -: {"src_hid": "$src_hid", "timestamp": "$syslog_timestamp", "dvchost": "$dvchost", "campaign_id": "$campaign_id", "reason": "$reason", "src_name": "$src_name", "campaign_name": "$campaign_name", "campaign_link": "$campaign_link", "headend_addr": "$headend_addr", "dest_name": "$dest_name", "dest_id": "$dest_id", "vectra_timestamp": "$vectra_timestamp", "src_ip": "$src_ip", "version": "$version", "action": "$action", "dest_ip": "$dest_ip", "det_id": "$det_id"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:campaigns:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_v2 -: {"source_ip": "$source_ip", "dvchost": "$dvchost", "version": "$version", "role": "$role", "user": "$user", "message": "$message", "vectra_timestamp": "$vectra_timestamp", "headend_addr": "$headend_addr", "result": "$result"}
@pytest.mark.addons("vectra")
def test_vectra_ai_audit_json(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_v2 -: {"source_ip": "$source_ip", "dvchost": "$dvchost", "version": "$version", "role": "$role", "user": "$user", "message": "$message", "vectra_timestamp": "$vectra_timestamp", "headend_addr": "$headend_addr", "result": "$result"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:audit:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# <13>Jan 16 11:51:35 xxxxxxx vectra_json_v2 -: {"vectra_timestamp": "$vectra_timestamp", "version": "$version", "result": "$result", "type": "$type", "source_ip": "$source_ip", "message": "$message", "dvchost": "$dvchost", "headend_addr": "$headend_addr"}
@pytest.mark.addons("vectra")
def test_vectra_ai_health(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now()
    _, bsd, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        '{{ mark }}{{ bsd }} {{ host }} vectra_json_v2 -: {"vectra_timestamp": "$vectra_timestamp", "version": "$version", "result": "$result", "type": "$type", "source_ip": "$source_ip", "message": "$message", "dvchost": "$dvchost", "headend_addr": "$headend_addr"}'
    )
    message = mt.render(mark="<13>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="vectra:cognito:health:json"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
