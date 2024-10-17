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

hostdict = str("/var/lib/syslog-ng/vps")


class vpsc_parse(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = SqliteDict(f"{hostdict}.sqlite", decode=restricted_decode, decode_key=restricted_decode_key)
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            host = log_message.get_as_str("HOST", "")
            self.logger.debug(f"vpsc.parse host={host}")
            fields = self.db[host]
            self.logger.debug(f"vpsc.parse host={host} fields={fields}")
            for k, v in fields.items():
                log_message[k] = v

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        self.logger.debug("vpsc.parse complete")
        return True


class vpsc_dest(LogDestination):
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
            host = log_message.get_as_str("HOST", "")
            fields = {}
            fields[".netsource.sc4s_vendor"] = log_message.get_as_str(
                "fields.sc4s_vendor"
            )
            fields[".netsource.sc4s_product"] = log_message.get_as_str(
                "fields.sc4s_product"
            )

            self.logger.debug(f"vpsc.send host={host} fields={fields}")
            if host in self.db:
                current = self.db[host]
                if current != fields:
                    self.db[host] = fields
            else:
                self.db[host] = fields

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
    pass