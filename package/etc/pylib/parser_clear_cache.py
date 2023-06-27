
import sys
import traceback
import socket
import struct

import time
try:
    import syslogng
except:
    pass

# def ip2int(addr):
#     return struct.unpack("!I", socket.inet_aton(addr))[0]

# def int2ip(addr):
#     return socket.inet_ntoa(struct.pack("!I", addr))

hostdict = str("/var/lib/syslog-ng/hostip.sqlite")

class clear_name_cache(object):
    def init(self, options):
        self.logger = syslogng.Logger()
        # self.db = SqliteDict(f"{hostdict}.sqlite")
        return True

    # def deinit(self):
    #     self.db.close()

    def parse(self, log_message):

        try:
            if os.path.isfile(hostdict):
                os.remove(hostdict)
                sample_file = open('/var/lib/syslog-ng/after_call','w+')
                sample_file.close()
        except:
            pass

        self.logger.debug(f'FixHostResolver::parse method executed')
        return True
