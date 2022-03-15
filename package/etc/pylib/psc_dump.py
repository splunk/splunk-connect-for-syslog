
import sys
import traceback
import socket
import struct
from rocksdict import Rdict,AccessType
import time


hostdict = str("/var/lib/syslog-ng/cache/hostip")

db = Rdict(hostdict,access_type=AccessType.read_only())
for k,v in db.items():
    print(f"key={k}={v}")