import re
import sys
import traceback

try:
    import syslogng
    from syslogng import LogParser
except:

    class LogParser:
        pass


class cef_kv(LogParser):
    def init(self, options):
        self.logger = syslogng.Logger()
        return True

    def parse(self, log_message):

        try:
            data = log_message.get_as_str(".metadata.cef.ext", "")

            rpairs = re.findall(r"([^=\s]+)=((?:[\\]=|[^=])+)(?:\s|$)", data)
            pairs = {}
            keys = []
            for p in rpairs:
                pairs[p[0]] = p[1]
                keys.append(p[0])

            cleanpairs = {}
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
                    pairs[k] = pairs[k].replace("\=", "=").replace("&&", "\n")

            for k, v in pairs.items():
                kc = k.replace(" ", "_").replace(".", "_")
                log_message[f".values.{kc}"] = v

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
            self.logger.debug(f"kvqf_parse.parse complete")
        return True
