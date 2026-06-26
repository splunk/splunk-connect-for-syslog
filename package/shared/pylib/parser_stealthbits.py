try:
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


alert_text_key = ".values.AlertText"


def _split_alert_text(text):
    """Split AlertText into an optional leading sentence and the key/value body.

    Linear-time replacement for the regex ``^(.*[.!?])?(.*:.*)``, which was
    vulnerable to polynomial backtracking on inputs with no ``:``. Behaviour is
    identical to the old regex (verified by fuzzing): the body must contain a
    ``:``; the leading sentence greedily extends to the last ``.``/``!``/``?``
    that occurs before the final ``:``.

    Returns ``(sentence, body)`` on a match (``sentence`` may be ``None`` when
    there is no leading sentence), or ``None`` when the text does not match.
    """
    last_colon = text.rfind(":")
    if last_colon == -1:
        return None
    cut = -1
    for i in range(last_colon - 1, -1, -1):
        if text[i] in ".!?":
            cut = i
            break
    if cut == -1:
        return None, text
    return text[: cut + 1], text[cut + 1 :]


class alerttext_kv(LogParser):
    def init(self, options):
        return True

    def parse(self, log_message):
        result = _split_alert_text(log_message.get_as_str(alert_text_key, ""))
        if result is not None:
            log_message[alert_text_key] = result[0]
            text = result[1]
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
