import sys
import traceback
import sqlite3

try:
    import syslogng
    from syslogng import LogParser, LogDestination
except Exception:

    class LogParser:
        pass

    class LogDestination:
        pass


hostdict = str("/var/lib/syslog-ng/vps.sqlite")


class vpsc_parse(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = sqlite3.connect(hostdict)
        self.cursor = self.db.cursor()
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            host = log_message.get_as_str("HOST", "")
            self.logger.debug(f"vpsc.parse host={host}")
            self.cursor.execute("SELECT fields FROM hosts WHERE host=?", (host,))
            result = self.cursor.fetchone()
            if result:
                fields = eval(result[0])
                self.logger.debug(f"vpsc.parse host={host} fields={fields}")
                for k, v in fields.items():
                    log_message[k] = v
            else:
                self.logger.debug(f"No fields found for host={host}")

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
            self.db = sqlite3.connect(hostdict)
            self.cursor = self.db.cursor()
            # Create table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS hosts (
                    host TEXT PRIMARY KEY,
                    fields TEXT
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
            host = log_message.get_as_str("HOST", "")
            fields = {}
            fields[".netsource.sc4s_vendor"] = log_message.get_as_str("fields.sc4s_vendor")
            fields[".netsource.sc4s_product"] = log_message.get_as_str("fields.sc4s_product")

            self.logger.debug(f"vpsc.send host={host} fields={fields}")
            self.cursor.execute("SELECT fields FROM hosts WHERE host=?", (host,))
            result = self.cursor.fetchone()
            if result:
                current = eval(result[0])
                if current != fields:
                    self.cursor.execute("UPDATE hosts SET fields=? WHERE host=?", (str(fields), host))
            else:
                self.cursor.execute("INSERT INTO hosts (host, fields) VALUES (?, ?)", (host, str(fields)))
            self.db.commit()

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
