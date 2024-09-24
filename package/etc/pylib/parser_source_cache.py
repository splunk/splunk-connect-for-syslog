import sys
import traceback
import socket
import struct
import sqlite3

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


hostdict = "/var/lib/syslog-ng/hostip.sqlite"


class psc_parse(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = sqlite3.connect(hostdict)
        self.cursor = self.db.cursor()
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            ipaddr = log_message.get_as_str("SOURCEIP", "", repr="internal")
            ip_int = ip2int(ipaddr)
            self.logger.debug(f"psc.parse sourceip={ipaddr} int={ip_int}")
            self.cursor.execute("SELECT host FROM hosts WHERE ip_int=?", (ip_int,))
            result = self.cursor.fetchone()
            if result:
                name = result[0]
                self.logger.debug(f"psc.parse host={name}")
                log_message["HOST"] = name
            else:
                self.logger.debug(f"No entry found for sourceip={ipaddr}")

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
            self.db = sqlite3.connect(hostdict)
            self.cursor = self.db.cursor()
            # Create table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS hosts (
                    ip_int INTEGER PRIMARY KEY,
                    host TEXT
                )
            """)
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
            host = log_message["HOST"]
            self.logger.debug(f'psc.send sourceip={ipaddr} int={ip_int} host={host}')
            self.cursor.execute("SELECT host FROM hosts WHERE ip_int=?", (ip_int,))
            result = self.cursor.fetchone()
            if result:
                current = result[0]
                if current != host:
                    self.cursor.execute("UPDATE hosts SET host=? WHERE ip_int=?", (host, ip_int))
            else:
                self.cursor.execute("INSERT INTO hosts (ip_int, host) VALUES (?, ?)", (ip_int, host))

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
    db = sqlite3.connect(hostdict)
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
            ip_int INTEGER PRIMARY KEY,
            host TEXT
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO hosts (ip_int, host) VALUES (?, ?)", (0, "seed"))
    db.commit()
    db.close()
