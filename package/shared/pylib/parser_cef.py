import re
import sys
import traceback

try:
    import syslogng
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


_CEF_KEY_RE = re.compile(r"(?:^|\s)([^\s=]+?)(?<!\\)=")


def _parse_cef_ext(data):
    """Split a CEF extension string into ``(key, value)`` pairs.

    A key is a run of non-space characters up to the first unescaped ``=``; its
    value is the text up to the next key (or end of string). ``\\=`` is treated
    as an in-value equals, and empty values are dropped.
    """
    matches = list(_CEF_KEY_RE.finditer(data))
    pairs = []
    for i, m in enumerate(matches):
        value_end = matches[i + 1].start() if i + 1 < len(matches) else len(data)
        value = data[m.end() : value_end]
        if value:
            pairs.append((m.group(1), value))
    return pairs


class cef_kv(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        return True

    def parse(self, log_message):

        try:
            data = log_message.get_as_str(".metadata.cef.ext", "")

            rpairs = _parse_cef_ext(data)
            pairs = {}
            keys = []
            for p in rpairs:
                pairs[p[0]] = p[1]
                keys.append(p[0])

            for k in keys:
                if k.endswith("Label"):
                    vk = k.rstrip("Label")
                    if k in pairs:
                        l = pairs[k]
                        if vk in pairs:
                            pairs[l] = pairs[vk]
                            del pairs[vk]
                        del pairs[k]
                elif k == "rawEvent":
                    pairs[k] = pairs[k].replace(r"\=", "=").replace("&&", "\n")

            for k, v in pairs.items():
                kc = k.replace(" ", "_").replace(".", "_")
                log_message[f".values.{kc}"] = v

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False

        return True
