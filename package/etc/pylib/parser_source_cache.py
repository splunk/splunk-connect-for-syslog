import sys
import traceback
import socket
import struct
from sqlitedict import SqliteDict

import time

try:
    import syslogng
except:
    pass


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


hostdict = str("/var/lib/syslog-ng/hostip")


class psc_parse(syslogng.LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = SqliteDict(f"{hostdict}.sqlite")
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            ipaddr = log_message.get_as_str("SOURCEIP", "", repr="internal")
            ip_int = ip2int(ipaddr)
            self.logger.debug(f"psc.parse sourceip={ipaddr} int={ip_int}")
            name = self.db[ip_int]
            self.logger.debug(f"psc.parse host={name}")
            log_message["HOST"] = name

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        self.logger.debug(f"psc.parse complete")
        return True


class psc_dest(syslogng.LogDestination):
    def init(self, options):
        self.logger = syslogng.Logger()
        try:
            self.db = SqliteDict(f"{hostdict}.sqlite", autocommit=True)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        return True

    def deinit(self):
        """Close the connection to the target service"""
        self.db.commit()
        self.db.close()

    def send(self, log_message):
        try:
            ipaddr = log_message.get_as_str("SOURCEIP", "", repr="internal")
            ip_int = ip2int(ipaddr)
            self.logger.debug(
                f'psc.send sourceip={ipaddr} int={ip_int} host={log_message["HOST"]}'
            )
            if ip_int in self.db:
                current = self.db[ip_int]
                if current != log_message["HOST"]:
                    self.db[ip_int] = log_message["HOST"]
            else:
                self.db[ip_int] = log_message["HOST"]

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        self.logger.debug("psc.send complete")
        return True

    def flush(self):
        self.db.commit()
        return True


if __name__ == "__main__":
    db = SqliteDict(f"{hostdict}.sqlite", autocommit=True)
    db[0] = "seed"
    db.commit()
    db.close()
