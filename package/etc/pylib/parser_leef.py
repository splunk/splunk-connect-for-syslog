import re
import binascii

try:
    import syslogng
    from syslogng import LogParser
except Exception:

    class LogParser:
        pass


class leef_kv(LogParser):
    def init(self, options):
        self.regex = r"( ?(?:[A-Z]{2,4}T|HAEC|IDLW|MSK|NT|UTC|THA))"
        self.logger = syslogng.Logger()
        return True
    
    def parse_message_from_pair(self, pair, log_message):
        f, v = pair.split("=", 1)
        if f == "devTime":
            log_message[".leef." + f] = re.sub(
                self.regex, "", v, 0, re.MULTILINE
            )
        else:
            log_message[".leef." + f] = v

    def parse_v1(self, log_message, structure, pairs, separator):
        separator = "\t"
        pairs = event.split(separator)
        if len(pairs) < 4:
            separator = "|"
            pairs = structure[5:]
            event = "\t".join(pairs)
            log_message[".leef.event"] = event

    def parse_v2(self, event, pairs, structure, separator):
        # V2 messages should always provide the sep but some fail do comply
        # with the format spec if they don't assume tab
        if len(structure) == 6 or not structure[5]:
            separator = "\t"
            pairs = event.split(separator)
        else:
            separator = structure[5]
            if separator.startswith("0"):
                separator = separator[1:]
            pairs = event.split(separator)

    def parse(self, log_message):
        try:
            msg = log_message.get_as_str("MESSAGE", "")
            # All LEEF message are | separated super structures
            structure = msg.split("|")

            # Indexed fields for Splunk
            log_message[".metadata.leef.version"] = structure[0][5:]
            log_message[".metadata.leef.vendor"] = structure[1]
            log_message[".metadata.leef.product"] = structure[2]
            log_message[".metadata.leef.product_version"] = structure[3]
            log_message[".metadata.leef.EventID"] = structure[4]

            # We just want the event field
            event = structure[len(structure) - 1]
            log_message[".leef.event"] = event

            separator= ""
            pairs = []

            # V1 will always use tab
            if structure[0][5:].startswith("1"):
                lv = "1"
                self.parse_v1(log_message, structure, pairs, separator)
            else:
                lv = "2"
                self.parse_v2(event, pairs, structure, separator)

            if separator.startswith("x"):
                hex_sep = f"0{separator.lower()}"
            else:
                hex_sep = f'0x{binascii.b2a_hex(separator.encode("utf-8")).decode("utf-8").lower()}'
            if structure[0][5:].startswith("1"):
                log_message[".splunk.sourcetype"] = f"LEEF:{lv}"
            else:
                log_message[".splunk.sourcetype"] = f"LEEF:{lv}:{hex_sep}"
            log_message[".splunk.source"] = f"{structure[1]}:{structure[2]}"
            log_message["fields.sc4s_vendor"] = structure[1]
            log_message["fields.sc4s_product"] = structure[2]

            for p in pairs:
                self.parse_message_from_pair(p, log_message)
        except Exception as e:
            log_message[".metadata.leef.exception"] = str(e)

        # return True, other way message is dropped
        return True
