import re

try:
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


regex = r"^(.*[\.\!\?])?(.*:.*)"
alert_text_key = ".values.AlertText"


class alerttext_kv(LogParser):
    def init(self, options):
        return True

    def parse(self, log_message):
        match = re.search(regex, log_message.get_as_str(alert_text_key, ""))
        if match:
            log_message[alert_text_key] = match.groups()[0]
            text = match.groups()[1]
        else:
            text = log_message.get_as_str(alert_text_key, "")
            log_message[alert_text_key] = ""

        pairs = text.split("; ")

        if len(pairs) == 0:
            return False
        for p in pairs:
            k, v = p.split(": ")
            cleank = k.replace(" ", "_").replace(".", "_")
            log_message[f".values.AlertTextValues.{cleank}"] = v.strip()
        return True