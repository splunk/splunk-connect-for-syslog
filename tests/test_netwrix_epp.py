# Copyright 2024 Splunk, Inc.
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

# <129>1 2024-02-22T13:11:24+00:00 hostname EPP-1.1.1.1 23203 - - EPP IP - xxxxxxx.hosted.endpointprotector.com - Device Control - File Read: [Log ID] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [Event Name] File Read | [Client Computer] XXXXXXXXXX | [IP Address] 1.1.1.1 | [MAC Address] XX-XX-XX-XX-XX-XX | [Serial Number]  | [OS] Windows 10 Enterprise x64 22H2  (XXXXX.XXXX) | [Client User] XXXXXXXX | [Device Type] Serial ATA Controller | [Device] Intel(R) 300 Series Chipset Family SATA AHCI Controller/Intel Corp. | [Device VID] XXXXX | [Device PID] XXXX | [Device Serial] XXXXXXXXXXXXXXX | [EPP Client Version] 6.1.0.6 | [File Name] X:/PATH/meta.json | [File Hash] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [File Type] .json file | [File Size] 276 | [Justification]  | [Time Interval]  | [Date/Time(Server)] 2024-02-22 13:11:24 | [Date/Time(Client)] 2024-02-22 08:11:16 | [Date/Time(Server UTC)] 2024-02-22T13:11:24Z | [Date/Time(Client UTC)] 2024-02-22T13:11:16Z

@pytest.mark.addons("netwrix")
def test_netwrix(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    event = "{{ mark }}1 {{ timestamp }} {{ host }} EPP-1.1.1.1 23203 - - EPP IP - xxxxxxx.hosted.endpointprotector.com - Device Control - File Read: [Log ID] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [Event Name] File Read | [Client Computer] XXXXXXXXXX | [IP Address] 1.1.1.1 | [MAC Address] XX-XX-XX-XX-XX-XX | [Serial Number]  | [OS] Windows 10 Enterprise x64 22H2  (XXXXX.XXXX) | [Client User] XXXXXXXX | [Device Type] Serial ATA Controller | [Device] Intel(R) 300 Series Chipset Family SATA AHCI Controller/Intel Corp. | [Device VID] XXXXX | [Device PID] XXXX | [Device Serial] XXXXXXXXXXXXXXX | [EPP Client Version] 6.1.0.6 | [File Name] X:/PATH/meta.json | [File Hash] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [File Type] .json file | [File Size] 276 | [Justification]  | [Time Interval]  | [Date/Time(Server)] 2024-02-22 13:11:24 | [Date/Time(Client)] 2024-02-22 08:11:16 | [Date/Time(Server UTC)] 2024-02-22T13:11:24Z | [Date/Time(Client UTC)] 2024-02-22T13:11:16Z"

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<129>", timestamp=iso, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="netwrix:epp" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1


# 952 <129>1 2024-02-22T13:11:24+00:00 hostname EPP-1.1.1.1 23203 - - EPP IP - xxxxxxx.hosted.endpointprotector.com - Device Control - File Read: [Log ID] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [Event Name] File Read | [Client Computer] XXXXXXXXXX | [IP Address] 1.1.1.1 | [MAC Address] XX-XX-XX-XX-XX-XX | [Serial Number]  | [OS] Windows 10 Enterprise x64 22H2  (XXXXX.XXXX) | [Client User] XXXXXXXX | [Device Type] Serial ATA Controller | [Device] Intel(R) 300 Series Chipset Family SATA AHCI Controller/Intel Corp. | [Device VID] XXXXX | [Device PID] XXXX | [Device Serial] XXXXXXXXXXXXXXX | [EPP Client Version] 6.1.0.6 | [File Name] X:/PATH/meta.json | [File Hash] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [File Type] .json file | [File Size] 276 | [Justification]  | [Time Interval]  | [Date/Time(Server)] 2024-02-22 13:11:24 | [Date/Time(Client)] 2024-02-22 08:11:16 | [Date/Time(Server UTC)] 2024-02-22T13:11:24Z | [Date/Time(Client UTC)] 2024-02-22T13:11:16Z

@pytest.mark.addons("netwrix")
def test_netwrix_framed(
    record_property,  get_host_key, setup_splunk, setup_sc4s
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    event = "{{ mark }}1 {{ timestamp }} {{ host }} EPP-1.1.1.1 23203 - - EPP IP - xxxxxxx.hosted.endpointprotector.com - Device Control - File Read: [Log ID] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [Event Name] File Read | [Client Computer] XXXXXXXXXX | [IP Address] 1.1.1.1 | [MAC Address] XX-XX-XX-XX-XX-XX | [Serial Number]  | [OS] Windows 10 Enterprise x64 22H2  (XXXXX.XXXX) | [Client User] XXXXXXXX | [Device Type] Serial ATA Controller | [Device] Intel(R) 300 Series Chipset Family SATA AHCI Controller/Intel Corp. | [Device VID] XXXXX | [Device PID] XXXX | [Device Serial] XXXXXXXXXXXXXXX | [EPP Client Version] 6.1.0.6 | [File Name] X:/PATH/meta.json | [File Hash] XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX | [File Type] .json file | [File Size] 276 | [Justification]  | [Time Interval]  | [Date/Time(Server)] 2024-02-22 13:11:24 | [Date/Time(Client)] 2024-02-22 08:11:16 | [Date/Time(Server UTC)] 2024-02-22T13:11:24Z | [Date/Time(Client UTC)] 2024-02-22T13:11:16Z"

    mt = env.from_string(event + "\n")
    message = mt.render(mark="<129>", timestamp=iso, host=host)
    ietf = f"{len(message)} {message}"

    sendsingle(ietf, setup_sc4s[0], setup_sc4s[1][601])

    st = env.from_string(
        'search index=netops _time={{ epoch }} sourcetype="netwrix:epp" host="{{ host }}"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1