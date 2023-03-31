import re
try:
    import syslogng
except:
    pass

regex = r"^(.*[\.\!\?])?(.*:.*)"

class alerttext_kv(syslogng.LogParser):
    def init(self, options):
        return True

    def parse(self, log_message):
        match = re.search(regex, log_message[".values.AlertText"].decode("utf-8"))
        if match:
            log_message[".values.AlertText"] = match.groups()[0]
            text = match.groups()[1]
        else:
            text = log_message[".values.AlertText"].decode("utf-8")
            log_message[".values.AlertText"] = ""

        pairs = text.split("; ")

        if len(pairs) == 0:
            return False
        for p in pairs:
            k, v = p.split(": ")
            cleank = k.replace(" ", "_").replace(".", "_")
            log_message[f".values.AlertTextValues.{cleank}"] = v.strip()
        return True
