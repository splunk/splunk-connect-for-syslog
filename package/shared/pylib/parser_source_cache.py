import traceback
import socket
import struct
from sqlitedict import SqliteDict

try:
    import syslogng
    from syslogng import LogParser, LogDestination
except Exception:

    class LogParser:
        pass

    class LogDestination:
        pass


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
        self.db = SqliteDict(f"{hostdict}.sqlite")
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            ipaddr = log_message.get_as_str("SOURCEIP", "", repr="internal")
            ip_int = ip2int(ipaddr)
            self.logger.debug(f"psc.parse sourceip={ipaddr} int={ip_int}")
            try:
                name = self.db[ip_int]
            except KeyError:
                return False
            self.logger.debug(f"psc.parse host={name}")
            log_message["HOST"] = name

        except Exception:
            self.logger.debug(traceback.format_exc())
            return False
        self.logger.debug("psc.parse complete")
        return True


class psc_dest(LogDestination):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = None
        return True

    def open(self):
        try:
            self.db = SqliteDict(f"{hostdict}.sqlite", autocommit=False)
        except Exception:
            self.logger.debug(traceback.format_exc())
            return False
        return True

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None

    def deinit(self):
        self.close()

    def send(self, log_message):
        try:
            ipaddr = log_message.get_as_str("SOURCEIP", "", repr="internal")
            if not ipaddr:
                self.logger.debug(
                    f"psc.send skipped: invalid cache key sourceip={ipaddr!r} "
                )
                return self.SUCCESS

            try:
                host = log_message["HOST"]
            except KeyError:
                self.logger.debug("psc.send skipped: HOST is missing")
                return self.SUCCESS

            if not host:
                self.logger.debug(
                    f"psc.send skipped: HOST is empty"
                )
                return self.SUCCESS

            try:
                ip_int = ip2int(ipaddr)
            except OSError:
                self.logger.debug(
                    f"psc.send skipped: invalid SOURCEIP sourceip={ipaddr!r}"
                )
                return self.SUCCESS

            try:
                current = self.db[ip_int]
            except KeyError:
                self.db[ip_int] = host
            else:
                if current != host:
                    self.db[ip_int] = host
        except Exception:
            self.logger.debug(traceback.format_exc())
            return self.ERROR
        self.logger.debug("psc.send complete")
        return self.QUEUED

    def flush(self):
        try:
            self.db.commit()
        except Exception:
            self.logger.debug(traceback.format_exc())
            return self.ERROR
        return self.SUCCESS


if __name__ == "__main__":
    db = SqliteDict(f"{hostdict}.sqlite", autocommit=True)
    db[0] = "seed"
    db.commit()
    db.close()
