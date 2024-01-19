# Copyright 2024 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape
import datetime
import pytest

from .sendmessage import sendsingle
from .splunkutils import  splunk_single


env = Environment(autoescape=select_autoescape(default_for_string=False))

# <30>1 2012-12-07T21:44:04.875Z t3-normaluser.i.vormetric.com vee-FS 0 CGP2603I [CGP@21513 sev="INFO" msg="Audit access" cat="\[AUDIT\]" pol="normaluser-only-aes256" uinfo="normaluser,uid=2001,gid=1" sproc="/usr/bin/cat" act="read_attr" gp="/export/home/normaluser/test" filePath="test.txt" denyStr="PERMIT" showStr="Code (1M)"]
# <30>1 2023-12-11T14:30:02.217Z host.domain.com vee-fs@Prod 20643922 CGP2602E [CGP@21513 sev="ERROR" msg="Reject access" cat="\[LEARN MODE\]" pol="C-TCUPNEW-PROD-Operational" uinfo="oracle,uid=43047 (User Not Authenticated)" sproc="/usr/bin/wc" act="read_file" gp="/OCM24P/trace" filePath="/alert_OCM24P.log" key="X-XXXX-PROD_XXXXXXXX" denyStr="DENIED" showStr="Code (XX,XX,XX,XX,XX,XX,XX,XX,XX)"]
# <30>1 2023-12-11T14:30:04.968Z 1.1.1.1 vee-fs@Prod 15925396 CGP2610E [CGP@21513 sev="ERROR" msg="Reject rename" cat="\[LEARN MODE\]" pol="C-SMART-PERFDR-SYB-Operational" uinfo="sybase,uid=4010 (User Not Authenticated)" sproc="/usr/bin/mv" act="rename" gp="/syb_dmp" oldFilePath="/temp.dmp" filePath="/DISTR13/SCLI.2023-12-11.09:30:04.trandmp" denyStr="DENIED" showStr="Code (XX,XX,XX,XX,XX,XX,XX,XX,XX)"]
# <30>1 2023-12-11T14:21:50.096Z host.domain.com dsm@NonProd 2572 COM0313E [COM@21513 sev="ERROR" msg="failed to contact host" shost="shost.domain.com" nexttime="Mon Dec 11 10:54:54 PST 2023"]

test_data = [
    '{{ mark }}1 {{ timestamp }} {{ host }} vee-FS 0 CGP2603I [CGP@21513 sev="INFO" msg="Audit access" cat="\[AUDIT\]" pol="normaluser-only-aes256" uinfo="normaluser,uid=2001,gid=1" sproc="/usr/bin/cat" act="read_attr" gp="/export/home/normaluser/test" filePath="test.txt" denyStr="PERMIT" showStr="Code (1M)"]',
    '{{ mark }}1 {{ timestamp }} {{ host }} vee-fs@Prod 20643922 CGP2602E [CGP@21513 sev="ERROR" msg="Reject access" cat="\[LEARN MODE\]" pol="C-TCUPNEW-PROD-Operational" uinfo="oracle,uid=43047 (User Not Authenticated)" sproc="/usr/bin/wc" act="read_file" gp="/OCM24P/trace" filePath="/alert_OCM24P.log" key="X-XXXX-PROD_XXXXXXXX" denyStr="DENIED" showStr="Code (XX,XX,XX,XX,XX,XX,XX,XX,XX)"]',
    '{{ mark }}1 {{ timestamp }} {{ host }} vee-fs@Prod 15925396 CGP2610E [CGP@21513 sev="ERROR" msg="Reject rename" cat="\[LEARN MODE\]" pol="C-SMART-PERFDR-SYB-Operational" uinfo="sybase,uid=4010 (User Not Authenticated)" sproc="/usr/bin/mv" act="rename" gp="/syb_dmp" oldFilePath="/temp.dmp" filePath="/DISTR13/SCLI.2023-12-11.09:30:04.trandmp" denyStr="DENIED" showStr="Code (XX,XX,XX,XX,XX,XX,XX,XX,XX)"]',
    '{{ mark }}1 {{ timestamp }} {{ host }} dsm@NonProd 2572 COM0313E [COM@21513 sev="ERROR" msg="failed to contact host" shost="shost.domain.com" nexttime="Mon Dec 11 10:54:54 PST 2023"]',
]

@pytest.mark.addons("thales")
@pytest.mark.parametrize("event", test_data)
def test_vormetric(record_property, get_host_key, setup_splunk, setup_sc4s, event):
    host = get_host_key

    dt = datetime.datetime.now()
    timestamp = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    epoch = dt.astimezone().strftime("%s.%f")[:-3]
    
    mt = env.from_string(event)

    message = mt.render(mark="<30>", timestamp=timestamp, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netauth  host={{ host }} sourcetype="thales:vormetric"'
    )
    search = st.render(
        epoch=epoch, host=host
    )

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
