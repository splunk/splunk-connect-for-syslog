import sys
import traceback
import socket
import struct
from sqlitedict import SqliteDict

import time

try:
    import syslogng
    from syslogng import LogParser, LogDestination
except Exception:

    class LogParser:
        pass

    class LogDestination:
        pass

import builtins
import io
import pickle
from base64 import b64decode

safe_builtins = {
    'range',
    'complex',
    'set',
    'frozenset',
    'slice',
}

class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        # Only allow safe classes from builtins.
        if module == "builtins" and name in safe_builtins:
            return getattr(builtins, name)
        # Forbid everything else.
        raise pickle.UnpicklingError("global '%s.%s' is forbidden" %
                                     (module, name))

def restricted_loads(s):
    """Helper function analogous to pickle.loads()."""
    return RestrictedUnpickler(io.BytesIO(s)).load()

def restricted_decode(obj):
    """Overwrite sqlitedict.decode to prevent code injection."""
    return restricted_loads(bytes(obj))

def restricted_decode_key(key):
    """Overwrite sqlitedict.decode_key to prevent code injection."""
    return restricted_loads(b64decode(key.encode("ascii")))


def ip2int(addr):
    ip4_to_int = lambda addr: struct.unpack("!I", socket.inet_aton(addr))[0]
    
    def ip6_to_int(addr):
        ip6 = socket.inet_pton(socket.AF_INET6, addr)
        a, b = struct.unpack(">QQ", ip6)
        return (a << 64) | b
    
    try:
        return ip4_to_int(addr)
    except OSError:
        return ip6_to_int(addr)


def int2ip(addr):
    int_to_ip4 = lambda addr: socket.inet_ntoa(struct.pack("!I", addr))

    def int_to_ip6(num):
        a = (num >> 64) & 0xFFFFFFFFFFFFFFFF
        b = num & 0xFFFFFFFFFFFFFFFF
        ip6 = struct.pack(">QQ", a, b)
        addr = socket.inet_ntop(socket.AF_INET6, ip6)
        return addr
    
    try:
        return int_to_ip4(addr)
    except struct.error:
        return int_to_ip6(addr)


hostdict = str("/var/lib/syslog-ng/hostip")


class psc_parse(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = SqliteDict(f"{hostdict}.sqlite", decode=restricted_decode, decode_key=restricted_decode_key)
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

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        self.logger.debug("psc.parse complete")
        return True


class psc_dest(LogDestination):
    def init(self, options):
        self.logger = syslogng.Logger()
        try:
            self.db = SqliteDict(f"{hostdict}.sqlite", autocommit=True, decode=restricted_decode, decode_key=restricted_decode_key)
        except Exception:
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

        except Exception:
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
    db = SqliteDict(f"{hostdict}.sqlite", autocommit=True, decode=restricted_decode, decode_key=restricted_decode_key)
    db[0] = "seed"
    db.commit()
    db.close()