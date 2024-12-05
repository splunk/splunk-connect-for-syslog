import sys
import traceback
import socket
import struct
from restricted_sqlitedict import SqliteDict


hostdict = str("/var/lib/syslog-ng/cache/hostip")
db = SqliteDict(f"{hostdict}.sqlite")

for k, v in db.items():
    print(f"key={k}={v}")
