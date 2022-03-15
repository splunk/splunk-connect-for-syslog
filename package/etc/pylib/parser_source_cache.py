
import sys
import traceback
import socket
import struct
from rocksdict import Rdict,AccessType,Options, WriteBatch, WriteOptions

import time
try:
    import syslogng
except:
    pass

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

hostdict = str("/var/lib/syslog-ng/cache/hostip")

class psc(object):
    def init(self, options):
        self.logger = syslogng.Logger()
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            db = Rdict(hostdict,access_type=AccessType.read_only())
            ipaddr = log_message["SOURCEIP"].decode("utf-8")
            ip_int = ip2int(ipaddr)
            self.logger.debug(f'psc.parse sourceip={ipaddr} int={ip_int}')
            name = db[ip_int]
            self.logger.debug(f'psc.parse host={name}')
            log_message["HOST"]=name

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug(''.join('!! ' + line for line in lines))
            return False
        self.logger.debug(f'psc.parse complete')
        return True

class psc_dest(object):
    def init(self, options):
        self.logger = syslogng.Logger()
        try:
            self.db = Rdict(hostdict)
        except:
            return False
        return True

    def deinit(self):
        """Close the connection to the target service"""
        self.db.flush()
        self.db.close()

    def send(self, log_message):
        try:
            ipaddr = log_message["SOURCEIP"].decode("utf-8")
            ip_int = ip2int(ipaddr)
            self.logger.debug(f'psc.send sourceip={ipaddr} int={ip_int} host={log_message["HOST"]}')
            if ip_int in self.db:
                current = self.db[ip_int]
                if current != log_message["HOST"]:
                    self.db[ip_int] =log_message["HOST"]    
            else:
                self.db[ip_int] =log_message["HOST"]
                
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug(''.join('!! ' + line for line in lines))
            return False
        self.logger.debug('psc.send complete')
        return True

    def flush(self):
        self.db.flush()

if __name__ == "__main__":
    db = Rdict(hostdict)
    db[0]="seed"
    db.close()
