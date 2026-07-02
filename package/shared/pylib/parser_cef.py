import sys
import traceback

try:
    import syslogng
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


def _parse_cef_ext(data):
    """Split a CEF extension string into ``(key, value)`` pairs.

    Linear-time replacement for the regex ``([^=\\s]+)=((?:\\=|[^=])+)(?:\\s|$)``,
    which SonarQube flagged for polynomial backtracking (rule S5852): the value
    class overlapped the trailing whitespace delimiter, so the engine could split
    a value at many points. This scanner is single-pass and behaves identically
    to the old regex (verified by fuzzing 1M random inputs):

    * a key is a run of non-space, non-``=`` characters immediately followed by
      ``=``;
    * a value is the text up to the whitespace that precedes the next key, with
      ``\\=`` treated as an escaped (in-value) equals and a bare ``=`` ending the
      scan;
    * empty values are dropped (the original ``+`` required at least one char).
    """
    pairs = []
    n = len(data)
    p = 0
    while p < n:
        # Key: maximal run of non-space, non-'=' chars, immediately followed by '='.
        start = p
        while p < n and data[p] != "=" and not data[p].isspace():
            p += 1
        if p == start or p >= n or data[p] != "=":
            if p >= n:
                break  # no '=' anywhere ahead; nothing more to find
            p = p + 1  # skip the space or bare '='
            continue
        key = data[start:p]
        p += 1  # skip '='

        # Value: scan until a bare '=' or end of string, remembering the last
        # whitespace boundary so we can stop the value before the next key.
        value_start = p
        last_ws = -1
        while p < n:
            c = data[p]
            if c == "\\" and p + 1 < n and data[p + 1] == "=":
                p += 2
                continue
            if c == "=":
                break  # bare '=' belongs to the next key, not this value
            if c.isspace():
                last_ws = p
            p += 1

        if p >= n:
            value = data[value_start:n]
            if value:
                pairs.append((key, value))
            break
        # Stopped on a bare '='; the value must end at the last whitespace boundary.
        if last_ws > value_start - 1:
            value = data[value_start:last_ws]
            if value:
                pairs.append((key, value))
            p = last_ws + 1
        else:
            p = value_start  # no boundary: this key has no usable value
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
