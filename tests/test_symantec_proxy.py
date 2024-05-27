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

# <134>1 2019-08-21T17:42:08.000z "sample_logs bluecoat[0]:SPLV5.1 c-ip=192.0.0.6 cs-bytes=6269 cs-categories="unavailable" cs-host=gg.hhh.iii.com cs-ip=192.0.0.6 cs-method=GET cs-uri-path=/Sample/abc-xyz-01.pqr_sample_Internal.crt/MFAwTqADAgEAMEcwRTBDMAkGBSsOAwIaBQAEFOoaVMtyzC9gObESY9g1eXf1VM8VBBTl1mBq2WFf4cYqBI6c08kr4S302gIKUCIZdgAAAAAnQA%3D%3D cs-uri-port=8000 cs-uri-scheme=http cs-User-Agent="ocspd/1.0.3" cs-username=user4 clientduration=0 rs-status=0 s-action=TCP_HIT s-ip=10.0.0.6 serveripservice.name="Explicit HTTP" service.group="Standard" s-supplier-ip=10.0.0.6 s-supplier-name=gg.hhh.iii.com sc-bytes=9469 sc-filter-result=OBSERVED sc-status=200 time-taken=20 x-bluecoat-appliance-name="10.0.0.6-sample_logs" x-bluecoat-appliance-primary-address=10.0.0.6 x-bluecoat-proxy-primary-address=10.0.0.6 x-bluecoat-transaction-uuid=35d24c931c0erecta-0003000012161a77e70-00042100041002145cc859ed c-url="http://randomserver:8000/en-US/app/examples/"
@pytest.mark.addons("broadcom")
def test_bluecoatproxySG_kv(record_property,  setup_splunk, setup_sc4s):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }}Z {{host}} bluecoat[0]: SPLV5.1 c-ip=192.0.0.6 cs-bytes=6269 cs-categories="unavailable" cs-host=gg.hhh.iii.com cs-ip=192.0.0.6 cs-method=GET cs-uri-path=/Sample/abc-xyz-01.pqr_sample_Internal.crt/MFAwTqADAgEAMEcwRTBDMAkGBSsOAwIaBQAEFOoaVMtyzC9gObESY9g1eXf1VM8VBBTl1mBq2WFf4cYqBI6c08kr4S302gIKUCIZdgAAAAAnQA%3D%3D cs-uri-port=8000 cs-uri-scheme=http cs-User-Agent="ocspd/1.0.3" cs-username=user4 clientduration=0 rs-status=0 s-action=TCP_HIT s-ip=10.0.0.6 serveripservice.name="Explicit HTTP" service.group="Standard" s-supplier-ip=10.0.0.6 s-supplier-name=gg.hhh.iii.com sc-bytes=9469 sc-filter-result=OBSERVED sc-status=200 time-taken=20 x-bluecoat-appliance-name="10.0.0.6-sample_logs" x-bluecoat-appliance-primary-address=10.0.0.6 x-bluecoat-proxy-primary-address=10.0.0.6 x-bluecoat-transaction-uuid=35d24c931c0erecta-0003000012161a77e70-00042100041002145cc859ed c-url="http://randomserver:8000/en-US/app/examples/"'
    )
    message = mt.render(mark="<134>", iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy host="{{ host }}" sourcetype="bluecoat:proxysg:access:kv"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#
# <111>1 $(date)T$(x-bluecoat-hour-utc):$(x-bluecoat-minute-utc):$(x-bluecoat-second-utc).000z $(x-bluecoat-appliance-name) bluecoat - splunk_format - c-ip=$(c-ip) Content-Type=$(quot)$(rs(Content-Type))$(quot) cs-auth-group=$(cs-auth-group) cs-bytes=$(cs-bytes) cs-categories=$(quot)$(cs-categories)$(quot) cs-host=$(cs-host) cs-ip=$(cs-ip) cs-method=$(cs-method) cs-uri-extension=$(cs-uri-extension) cs-uri-path=$(cs-uri-path) cs-uri-port=$(cs-uri-port) cs-uri-query=$(quot)$(cs-uri-query)$(quot) cs-uri-scheme=$(cs-uri-scheme) cs-User-Agent=$(quot)$(cs(User-Agent))$(quot) cs-username=$(cs-username) dnslookup-time=$(dnslookup-time) duration=$(duration) rs-status=$(rs-status) rs-version=$(rs-version) rs_Content_Type=$(rs-Content-Type) s-action=$(s-action) s-ip=$(s-ip) service.name=$(service.name) service.group=$(service.group) s-supplier-ip=$(s-supplier-ip) s-supplier-name=$(s-supplier-name) sc-bytes=$(sc-bytes) sc-filter-result=$(sc-filter-result) sc-filter-result=$(sc-filter-result) sc-status=$(sc-status) time-taken=$(time-taken) x-bluecoat-appliance-name=$(x-bluecoat-appliance-name) x-bluecoat-appliance-primary-address=$(x-bluecoat-appliance-primary-address) x-bluecoat-application-name=$(x-bluecoat-application-name) x-bluecoat-application-operation=$(x-bluecoat-application-operation) x-bluecoat-proxy-primary-address=$(x-bluecoat-proxy-primary-address) x-bluecoat-transaction-uuid=$(x-bluecoat-transaction-uuid) x-exception-id=$(x-exception-id) x-virus-id=$(x-virus-id) c-url=$(quot)$(url)$(quot) cs-Referer=$(quot)$(cs(Referer))$(quot) c-cpu=$(c-cpu) c-uri-pathquery=$(c-uri-pathquery) connect-time=$(connect-time) cs-auth-groups=$(cs-auth-groups) cs-headerlength=$(cs-headerlength) cs-threat-risk=$(cs-threat-risk) r-ip=$(r-ip) r-supplier-ip=$(r-supplier-ip) rs-time-taken=$(rs-time-taken) rs-server=$(rs(server)) s-connect-type=$(s-connect-type) s-icap-status=$(s-icap-status) s-sitename=$(s-sitename) s-source-port=$(s-source-port) s-supplier-country=$(s-supplier-country) sc-Content-Encoding=$(sc(Content-Encoding)) sr-Accept-Encoding=$(sr(Accept-Encoding)) x-auth-credential-type=$(x-auth-credential-type) x-cookie-date=$(x-cookie-date) x-cs-certificate-subject=$(x-cs-certificate-subject) x-cs-connection-negotiated-cipher=$(x-cs-connection-negotiated-cipher) x-cs-connection-negotiated-cipher-size=$(x-cs-connection-negotiated-cipher-size) x-cs-connection-negotiated-ssl-version=$(x-cs-connection-negotiated-ssl-version) x-cs-ocsp-error=$(x-cs-ocsp-error) x-cs-Referer-uri=$(x-cs(Referer)-uri) x-cs-Referer-uri-address=$(x-cs(Referer)-uri-address) x-cs-Referer-uri-extension=$(x-cs(Referer)-uri-extension) x-cs-Referer-uri-host=$(x-cs(Referer)-uri-host) x-cs-Referer-uri-hostname=$(x-cs(Referer)-uri-hostname) x-cs-Referer-uri-path=$(x-cs(Referer)-uri-path) x-cs-Referer-uri-pathquery=$(x-cs(Referer)-uri-pathquery) x-cs-Referer-uri-port=$(x-cs(Referer)-uri-port) x-cs-Referer-uri-query=$(x-cs(Referer)-uri-query) x-cs-Referer-uri-scheme=$(x-cs(Referer)-uri-scheme) x-cs-Referer-uri-stem=$(x-cs(Referer)-uri-stem) x-exception-category=$(x-exception-category) x-exception-category-review-message=$(x-exception-category-review-message) x-exception-company-name=$(x-exception-company-name) x-exception-contact=$(x-exception-contact) x-exception-details=$(x-exception-details) x-exception-header=$(x-exception-header) x-exception-help=$(x-exception-help) x-exception-last-error=$(x-exception-last-error) x-exception-reason=$(x-exception-reason) x-exception-sourcefile=$(x-exception-sourcefile) x-exception-sourceline=$(x-exception-sourceline) x-exception-summary=$(x-exception-summary) x-icap-error-code=$(x-icap-error-code) x-rs-certificate-hostname=$(x-rs-certificate-hostname) x-rs-certificate-hostname-category=$(x-rs-certificate-hostname-category) x-rs-certificate-observed-errors=$(x-rs-certificate-observed-errors) x-rs-certificate-subject=$(x-rs-certificate-subject) x-rs-certificate-validate-status=$(x-rs-certificate-validate-status) x-rs-connection-negotiated-cipher=$(x-rs-connection-negotiated-cipher) x-rs-connection-negotiated-cipher-size=$(x-rs-connection-negotiated-cipher-size) x-rs-connection-negotiated-ssl-version=$(x-rs-connection-negotiated-ssl-version) x-rs-ocsp-error=$(x-rs-ocsp-error)
#
@pytest.mark.addons("broadcom")
def test_bluecoatproxySG_kv_5424(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }}1 {{ iso }}Z {{host}} bluecoat - splunk_format - c-ip=192.0.0.6 cs-bytes=6269 cs-categories="unavailable" cs-host=gg.hhh.iii.com cs-ip=192.0.0.6 cs-method=GET cs-uri-path=/Sample/abc-xyz-01.pqr_sample_Internal.crt/MFAwTqADAgEAMEcwRTBDMAkGBSsOAwIaBQAEFOoaVMtyzC9gObESY9g1eXf1VM8VBBTl1mBq2WFf4cYqBI6c08kr4S302gIKUCIZdgAAAAAnQA%3D%3D cs-uri-port=8000 cs-uri-scheme=http cs-User-Agent="ocspd/1.0.3" cs-username=user4 clientduration=0 rs-status=0 s-action=TCP_HIT s-ip=10.0.0.6 serveripservice.name="Explicit HTTP" service.group="Standard" s-supplier-ip=10.0.0.6 s-supplier-name=gg.hhh.iii.com sc-bytes=9469 sc-filter-result=OBSERVED sc-status=200 time-taken=20 x-bluecoat-appliance-name="10.0.0.6-sample_logs" x-bluecoat-appliance-primary-address=10.0.0.6 x-bluecoat-proxy-primary-address=10.0.0.6 x-bluecoat-transaction-uuid=35d24c931c0erecta-0003000012161a77e70-00042100041002145cc859ed c-url="http://randomserver:8000/en-US/app/examples/"'
    )
    message = mt.render(mark="<134>", iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netproxy host="{{ host }}" sourcetype="bluecoat:proxysg:access:kv"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

#
# <111>1 $(date)T$(x-bluecoat-hour-utc):$(x-bluecoat-minute-utc):$(x-bluecoat-second-utc).000z $(x-bluecoat-appliance-name) bluecoat - splunk_format - c-ip=$(c-ip) Content-Type=$(quot)$(rs(Content-Type))$(quot) cs-auth-group=$(cs-auth-group) cs-bytes=$(cs-bytes) cs-categories=$(quot)$(cs-categories)$(quot) cs-host=$(cs-host) cs-ip=$(cs-ip) cs-method=$(cs-method) cs-uri-extension=$(cs-uri-extension) cs-uri-path=$(cs-uri-path) cs-uri-port=$(cs-uri-port) cs-uri-query=$(quot)$(cs-uri-query)$(quot) cs-uri-scheme=$(cs-uri-scheme) cs-User-Agent=$(quot)$(cs(User-Agent))$(quot) cs-username=$(cs-username) dnslookup-time=$(dnslookup-time) duration=$(duration) rs-status=$(rs-status) rs-version=$(rs-version) rs_Content_Type=$(rs-Content-Type) s-action=$(s-action) s-ip=$(s-ip) service.name=$(service.name) service.group=$(service.group) s-supplier-ip=$(s-supplier-ip) s-supplier-name=$(s-supplier-name) sc-bytes=$(sc-bytes) sc-filter-result=$(sc-filter-result) sc-filter-result=$(sc-filter-result) sc-status=$(sc-status) time-taken=$(time-taken) x-bluecoat-appliance-name=$(x-bluecoat-appliance-name) x-bluecoat-appliance-primary-address=$(x-bluecoat-appliance-primary-address) x-bluecoat-application-name=$(x-bluecoat-application-name) x-bluecoat-application-operation=$(x-bluecoat-application-operation) x-bluecoat-proxy-primary-address=$(x-bluecoat-proxy-primary-address) x-bluecoat-transaction-uuid=$(x-bluecoat-transaction-uuid) x-exception-id=$(x-exception-id) x-virus-id=$(x-virus-id) c-url=$(quot)$(url)$(quot) cs-Referer=$(quot)$(cs(Referer))$(quot) c-cpu=$(c-cpu) c-uri-pathquery=$(c-uri-pathquery) connect-time=$(connect-time) cs-auth-groups=$(cs-auth-groups) cs-headerlength=$(cs-headerlength) cs-threat-risk=$(cs-threat-risk) r-ip=$(r-ip) r-supplier-ip=$(r-supplier-ip) rs-time-taken=$(rs-time-taken) rs-server=$(rs(server)) s-connect-type=$(s-connect-type) s-icap-status=$(s-icap-status) s-sitename=$(s-sitename) s-source-port=$(s-source-port) s-supplier-country=$(s-supplier-country) sc-Content-Encoding=$(sc(Content-Encoding)) sr-Accept-Encoding=$(sr(Accept-Encoding)) x-auth-credential-type=$(x-auth-credential-type) x-cookie-date=$(x-cookie-date) x-cs-certificate-subject=$(x-cs-certificate-subject) x-cs-connection-negotiated-cipher=$(x-cs-connection-negotiated-cipher) x-cs-connection-negotiated-cipher-size=$(x-cs-connection-negotiated-cipher-size) x-cs-connection-negotiated-ssl-version=$(x-cs-connection-negotiated-ssl-version) x-cs-ocsp-error=$(x-cs-ocsp-error) x-cs-Referer-uri=$(x-cs(Referer)-uri) x-cs-Referer-uri-address=$(x-cs(Referer)-uri-address) x-cs-Referer-uri-extension=$(x-cs(Referer)-uri-extension) x-cs-Referer-uri-host=$(x-cs(Referer)-uri-host) x-cs-Referer-uri-hostname=$(x-cs(Referer)-uri-hostname) x-cs-Referer-uri-path=$(x-cs(Referer)-uri-path) x-cs-Referer-uri-pathquery=$(x-cs(Referer)-uri-pathquery) x-cs-Referer-uri-port=$(x-cs(Referer)-uri-port) x-cs-Referer-uri-query=$(x-cs(Referer)-uri-query) x-cs-Referer-uri-scheme=$(x-cs(Referer)-uri-scheme) x-cs-Referer-uri-stem=$(x-cs(Referer)-uri-stem) x-exception-category=$(x-exception-category) x-exception-category-review-message=$(x-exception-category-review-message) x-exception-company-name=$(x-exception-company-name) x-exception-contact=$(x-exception-contact) x-exception-details=$(x-exception-details) x-exception-header=$(x-exception-header) x-exception-help=$(x-exception-help) x-exception-last-error=$(x-exception-last-error) x-exception-reason=$(x-exception-reason) x-exception-sourcefile=$(x-exception-sourcefile) x-exception-sourceline=$(x-exception-sourceline) x-exception-summary=$(x-exception-summary) x-icap-error-code=$(x-icap-error-code) x-rs-certificate-hostname=$(x-rs-certificate-hostname) x-rs-certificate-hostname-category=$(x-rs-certificate-hostname-category) x-rs-certificate-observed-errors=$(x-rs-certificate-observed-errors) x-rs-certificate-subject=$(x-rs-certificate-subject) x-rs-certificate-validate-status=$(x-rs-certificate-validate-status) x-rs-connection-negotiated-cipher=$(x-rs-connection-negotiated-cipher) x-rs-connection-negotiated-cipher-size=$(x-rs-connection-negotiated-cipher-size) x-rs-connection-negotiated-ssl-version=$(x-rs-connection-negotiated-ssl-version) x-rs-ocsp-error=$(x-rs-ocsp-error)
#
@pytest.mark.addons("broadcom")
def test_bluecoatproxySG_syslog(
    record_property,  setup_splunk, setup_sc4s
):
    host = f"{shortuuid.ShortUUID().random(length=5).lower()}-{shortuuid.ShortUUID().random(length=5).lower()}"

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }}1 {{ iso }}Z {{host}} ProxySG - - - Some message does not matter what"'
    )
    message = mt.render(mark="<134>", iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netops host="{{ host }}" sourcetype="bluecoat:proxysg:access:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1

#
