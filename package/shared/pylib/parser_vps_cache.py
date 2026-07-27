import traceback
from sqlitedict import SqliteDict

try:
    import syslogng
    from syslogng import LogParser, LogDestination
except Exception:

    class LogParser:
        pass

    class LogDestination:
        pass


hostdict = str("/var/lib/syslog-ng/vps")


class vpsc_parse(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        self.db = SqliteDict(f"{hostdict}.sqlite")
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

        except KeyError:
            return False
        except Exception:
            self.logger.debug(traceback.format_exc())
            return False
        self.logger.debug("vpsc.parse complete")
        return True


class vpsc_dest(LogDestination):
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
            host = log_message.get_as_str("HOST", "")
            fields = {}
            fields[".netsource.sc4s_vendor"] = log_message.get_as_str(
                "fields.sc4s_vendor"
            )
            fields[".netsource.sc4s_product"] = log_message.get_as_str(
                "fields.sc4s_product"
            )

            self.logger.debug(f"vpsc.send host={host} fields={fields}")
            try:
                current = self.db[host]
            except KeyError:
                self.db[host] = fields
            else:
                if current != fields:
                    self.db[host] = fields
        except KeyError:
            return self.ERROR
        except Exception:
            self.logger.debug(traceback.format_exc())
            return self.ERROR
        self.logger.debug("vpsc.send complete")
        return self.QUEUED

    def flush(self):
        try:
            self.db.commit()
        except Exception:
            self.logger.debug(traceback.format_exc())
            return self.ERROR
        return self.SUCCESS
