import re

try:
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


alert_text_key = ".values.AlertText"

PAIR_RE = re.compile(r"([^:;]+):\s*([^;]*)")


class alerttext_kv(LogParser):
    def init(self, options):
        return True

    def parse(self, log_message):
        text = log_message.get_as_str(alert_text_key, "")
        pairs = [
            (m.group(1).strip(), m.group(2).strip()) for m in PAIR_RE.finditer(text)
        ]

        if not pairs:
            return True

        sentence = ""
        if pairs:
            first_key = pairs[0][0]
            cut = max(first_key.rfind("."), first_key.rfind("!"), first_key.rfind("?"))
            if cut != -1:
                sentence = first_key[: cut + 1]
                pairs[0] = (first_key[cut + 1 :].strip(), pairs[0][1])

        log_message[alert_text_key] = sentence
        for k, v in pairs:
            cleank = k.replace(" ", "_").replace(".", "_")
            log_message[f".values.AlertTextValues.{cleank}"] = v
        return True
