"""
simple syslog-ng Python parser example
resolves IP to hostname
value pair names are hard-coded
"""
import re
import socket
import os


class FixHostResolver(object):
    def parse(self, log_message):
        """
        Resolves IP to hostname
        """

        try:
            if os.getenv(f"SC4S_NAME_CACHE_CLEAR", "yes").lower() in [
                "true",
                "1",
                "t",
                "y",
                "yes",
            ] and os.path.exists("/var/lib/syslog-ng"):
                os.remove("/var/lib/syslog-ng/hostip.sqlite")
        except:
            pass


        # try to resolve the IP address
        try:
            ipaddr = log_message["SOURCEIP"].decode("utf-8")

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
