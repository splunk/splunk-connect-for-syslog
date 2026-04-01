# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility
import sys
import traceback
import re

try:
    import syslogng
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


regex = r"\"([^\"]+)\"=\"([^\"]+)\""


class kvqf_parse(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        return True

    def parse(self, log_message):
        try:
            matches = re.finditer(
                regex, log_message.get_as_str(".tmp.pairs", ""), re.MULTILINE
            )
            for _, match in enumerate(matches, start=1):
                k = match.groups()[0]
                v = match.groups()[1]
                log_message[f".values.{k}"] = v
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        self.logger.debug("kvqf_parse.parse complete")
        return True
