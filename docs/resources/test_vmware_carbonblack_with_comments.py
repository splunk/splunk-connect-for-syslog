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
# Below is a raw message
# <14>1 2022-03-30T11:17:11.900862-04:00 host - - - - Carbon Black App Control event:  text="File 'c:\program files\azure advanced threat protection sensor\0.0.0.0\winpcap\x86\packet.dll' [c4e671bf409076a6bf0897e8a11e6f1366d4b21bf742c5e5e116059c9b571363] would have blocked if the rule was not in Report Only mode." type="Policy Enforcement" subtype="Execution block (unapproved file)" hostname="CORP\USER" username="NT AUTHORITY\SYSTEM" date="3/30/2022 3:16:40 PM" ip_address="0.0.0.0" process="c:\program files\azure advanced threat protection sensor\0.0.0.0\microsoft.tri.sensor.updater.exe" file_path="c:\program files\azure advanced threat protection sensor\0.0.0.0\winpcap\x86\packet.dll" file_name="packet.dll" file_hash="c4e671bf409076a6bf0897e8a11e6f1366d4b21bf742c5e5e116059c9b571363" policy="High Enforcement - Domain Controllers" rule_name="Report read-only memory map operations on unapproved executables by .NET applications" process_key="00000433-0000-23d8-01d8-44491b26f203" server_version="0.0.0.0" file_trust="-2" file_threat="-2" process_trust="-2" process_threat="-2" prevalence="50"

# Don't forget to rename the function
def test_vmware_carbonblack_protect(
    record_property, setup_wordlist, setup_splunk, setup_sc4s
):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions for Checkpoint
    epoch = epoch[:-3]

    mt = env.from_string(
        # Extract mark, iso timestamp and host fields
        # Make sure all needed characters are escaped
        # If string contains single quotes wrap it in double qutes
        '{{ mark }} {{ iso }} {{ host }} - - - - Carbon Black App Control event:  text="File \'c:\\program files\\azure advanced threat protection sensor\\0.0.0.0\\winpcap\\x86\\packet.dll\' [c4e671bf409076a6bf0897e8a11e6f1366d4b21bf742c5e5e116059c9b571363] would have blocked if the rule was not in Report Only mode." type="Policy Enforcement" subtype="Execution block (unapproved file)" hostname="CORP\\USER" username="NT AUTHORITY\\SYSTEM" date="3/30/2022 3:16:40 PM" ip_address="0.0.0.0" process="c:\\program files\\azure advanced threat protection sensor\\0.0.0.0\\microsoft.tri.sensor.updater.exe" file_path="c:\\program files\\azure advanced threat protection sensor\\0.0.0.0\\winpcap\\x86\\packet.dll" file_name="packet.dll" file_hash="c4e671bf409076a6bf0897e8a11e6f1366d4b21bf742c5e5e116059c9b571363" policy="High Enforcement - Domain Controllers" rule_name="Report read-only memory map operations on unapproved executables by .NET applications" process_key="00000433-0000-23d8-01d8-44491b26f203" server_version="0.0.0.0" file_trust="-2" file_threat="-2" process_trust="-2" process_threat="-2" prevalence="50"'
    )
    message = mt.render(mark="<134>1", host=host, bsd=bsd, iso=iso, epoch=epoch)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        # Make sure you changed index and sourcetype properly
        'search _time={{ epoch }} index=epintel host="{{ host }}" sourcetype="vmware:cb:protect"'
    )
    search = st.render(epoch=epoch, bsd=bsd, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1
