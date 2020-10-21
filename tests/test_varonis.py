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

# <13>Aug 21 09:24:00 something CEF:0|Varonis Inc.|DatAdvantage|7.5.21|6001|File permissions added|5|rt=Oct 20 2020 07:57:10 cat=Alert cs2=Permissions granted directly to user in windows file system cs2Label=RuleName cn1=80 cn1Label=RuleID end=Oct 20 2020 07:51:13 duser=corp.xxxx.com\\first last dhost=xxxx filePath=D:\\Shared\\Global\\Clinical\\STATUS_20201020.XLSX fname=STATUS_20201020.XLSX act=File permissions added dvchost=LT-xxxxx dvc=10.1.3.81 outcome=Success msg=Full Control permissions for This object only (not inherited) was added to user xxx\\xxx on D:\\Shared\\Global\\Clinical\\STATUS_20201020.XLSX cs3= cs3Label=AttachmentName cs4= https://xxx.corp.xxxx.com:443/DatAdvantage/#/app/analytics/entity/Alert/xxx-18ad-4bd8-b2da-xxxx  cs4Label=AlertURL deviceCustomDate1= fileType= cs1= cs1Label=MailRecipient suser= cs5= cs5Label=MailboxAccessType cnt= cs6=Full Control cs6Label=ChangedPermissions oldFilePermission=None filePermission=Full Control dpriv=xxx\\xxxx start= externalId=bbxxxxxfd3b5c-18ad-4bd8-b2da-xxxxx


def test_varonis(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now()
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-7]

    mt = env.from_string(
        "{{ bsd }} {{ host }} vectra_cef -: CEF:0|Varonis Inc.|DatAdvantage|7.5.21|6001|File permissions added|5|rt=Oct 20 2020 07:57:10 cat=Alert cs2=Permissions granted directly to user in windows file system cs2Label=RuleName cn1=80 cn1Label=RuleID end=Oct 20 2020 07:51:13 duser=corp.xxxx.com\\first last dhost=xxxx filePath=D:\\Shared\\Global\\Clinical\\STATUS_20201020.XLSX fname=STATUS_20201020.XLSX act=File permissions added dvchost=LT-xxxxx dvc=10.1.3.81 outcome=Success msg=Full Control permissions for This object only (not inherited) was added to user xxx\\xxx on D:\\Shared\\Global\\Clinical\\STATUS_20201020.XLSX cs3= cs3Label=AttachmentName cs4= https://xxx.corp.xxxx.com:443/DatAdvantage/#/app/analytics/entity/Alert/xxx-18ad-4bd8-b2da-xxxx  cs4Label=AlertURL deviceCustomDate1= fileType= cs1= cs1Label=MailRecipient suser= cs5= cs5Label=MailboxAccessType cnt= cs6=Full Control cs6Label=ChangedPermissions oldFilePermission=None filePermission=Full Control dpriv=xxx\\xxxx start= externalId=bbxxxxxfd3b5c-18ad-4bd8-b2da-xxxxx\n"
    )
    message = mt.render(mark="<111>", bsd=bsd, host=host)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=main host="{{ host }}" sourcetype="veronis:ta"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

