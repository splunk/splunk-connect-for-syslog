import re

try:
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


alert_text_key = ".values.AlertText"

# Single-pass extraction of "key: value" pairs separated by "; ".
#   key   = [^:;]+  -> up to the pair's colon
#   value = [^;]*   -> up to the "; " separator (values keep their own ':',
#                      e.g. timestamps like "5/3/2022 1:26:00 AM")
# Both groups are negated character classes, so there is no backtracking: the
# match is linear in the input length (clears SonarQube S5852). This replaces
# the old ``^(.*[.!?])?(.*:.*)`` regex, whose greedy groups both backtracked and
# also mis-split values that contained a '.' (e.g. FQDNs), crashing the parser.
PAIR_RE = re.compile(r"([^:;]+):\s*([^;]*)")


class alerttext_kv(LogParser):
    def init(self, options):
        return True

    def parse(self, log_message):
        text = log_message.get_as_str(alert_text_key, "")
        pairs = [
            (m.group(1).strip(), m.group(2).strip()) for m in PAIR_RE.finditer(text)
        ]

        sentence = ""
        if pairs:
            first_key = pairs[0][0]
            # Any leading prose (e.g. "Activity still in process.") is glued to
            # the first key; split it off at the last sentence terminator.
            cut = max(first_key.rfind("."), first_key.rfind("!"), first_key.rfind("?"))
            if cut != -1:
                sentence = first_key[: cut + 1]
                pairs[0] = (first_key[cut + 1 :].strip(), pairs[0][1])

        log_message[alert_text_key] = sentence
        for k, v in pairs:
            cleank = k.replace(" ", "_").replace(".", "_")
            log_message[f".values.AlertTextValues.{cleank}"] = v
        return True
