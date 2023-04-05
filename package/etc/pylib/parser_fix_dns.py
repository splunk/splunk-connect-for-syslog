"""
simple syslog-ng Python parser example
resolves IP to hostname
value pair names are hard-coded
"""
import re
import socket

try:
    import syslogng
except:
    pass


class FixHostResolver(syslogng.LogParser):
    def parse(self, log_message):
        """
        Resolves IP to hostname
        """

        # try to resolve the IP address
        try:
            ipaddr = log_message.get_as_str("SOURCEIP", "", repr="internal")

            hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ipaddr)
            # print(ipaddr)
            # print(hostname)
            parts = str(hostname).split(".")
            name = parts[0]
            # print(name)
            if len(parts) > 1:
                log_message["HOST"] = name
        except:
            return False

        # return True, other way message is dropped
        return True
