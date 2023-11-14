# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import  splunk_single
from .timeutils import time_operations
import datetime
import pytest

env = Environment(autoescape=select_autoescape(default_for_string=False))

data = [
    r'{{ mark }} {{ iso }}Z {{ host }} KES|11.0.0.0 - GNRL_EV_APPLICATION_LAUNCH_DENIE [event@23668 p1="829fdcfa98cbcc63" p2="NT AUTHORITY\\SYSTEM" p3="00000000000000000000000000000000" p4="EAC00100000000000000000000000000" p5="{\"CertSerial\":\"\" ,\"CertThumbprint\":\"\" ,\"CertIssuer\":\"\" ,\"CertSubject\":\"\" ,\"ParentProcess\":\"\"}" p6="rm.bat" p7="C:\\Windows\\SysWOW64\\config\\systemprofile\\Citrix\\UpdaterBinaries\\rm.bat" p8=";DF4C7A695766C5592C6AAB9BD2D2EB87E0C73EAE9218955F61E507E564F26CFC" et="GNRL_EV_APPLICATION_LAUNCH_DENIED" tdn="Application Control" etdn="Application startup prohibited" hdn="WS11128" hip="10.21.203.17" gn="Bourbonnais Medical Plaza"] Event type: Application startup prohibited\r\nComment: At the next operating system restart, the prohibited process will be automatically blocked until Kaspersky Endpoint Security for Windows starts\r\nObject name: rm.bat\r\nPath to object: C:\Windows\SysWOW64\config\systemprofile\Citrix\UpdaterBinaries\rm.bat\r\nSHA256: df4c7a695766c5592c6aab9bd2d2eb87e0c73eae9218955f61e507e564f26cfc\r\nKL category: Uncategorized\r\nKL category source: Local databases\r\nUser: NT AUTHORITY\SYSTEM (Initiator)\r\nResult: Blocked\r\nRule category: Default Deny\r\nRule type: Not test',
]

@pytest.mark.parametrize("event", data)
@pytest.mark.addons("kaspersky")
def test_kaspersky(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="kaspersky:es"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


#CEF:0|KasperskyLab|SecurityCenter|13.2.0.1511|KLPRCI_TaskState|Completed successfully|1|rt=1647626887000 cs9=site location Bldg cs9Label=GroupName dhost=WS6465 dst=10.55.203.12 cs2=KES cs2Label=ProductName cs3=11.0.0.0 cs3Label=ProductVersion cs10=Uninstall EDR cs10Label=TaskName cs4=885 cs4Label=TaskId cn2=4 cn2Label=TaskNewState cn1=0 cn1Label=TaskOldState 
data2 = [
    r'{{ mark }} {{ iso }}Z {{ host }} CEF:0|KasperskyLab|SecurityCenter|13.2.0.1511|KLPRCI_TaskState|Completed successfully|1|rt=1647626887000 cs9=site location Bldg cs9Label=GroupName dhost=WS6465 dst=10.55.203.12 cs2=KES cs2Label=ProductName cs3=11.0.0.0 cs3Label=ProductVersion cs10=Uninstall EDR cs10Label=TaskName cs4=885 cs4Label=TaskId cn2=4 cn2Label=TaskNewState cn1=0 cn1Label=TaskOldState ',
]
@pytest.mark.parametrize("event", data2)
@pytest.mark.addons("kaspersky")
def test_kaspersky_cef(
    record_property,  get_host_key, setup_splunk, setup_sc4s, event
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<29>1", iso=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=epav host="{{ host }}" sourcetype="kaspersky:klprci"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1