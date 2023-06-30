
import os
from sqlitedict import SqliteDict

try:
    import syslogng
except:
    pass

hostdict = str("/var/lib/syslog-ng/hostip.sqlite")


class clear_name_cache(object):

    def parse(self, log_message):

        try:
            self.logger = syslogng.Logger()
            self.db = SqliteDict(hostdict, autocommit=True)
            sample_file = open('/var/lib/syslog-ng/Before_call.txt', 'w+')
            sample_file.close()
            self.db.clear()
            self.db.close()
            sample_file = open('/var/lib/syslog-ng/after_call.txt', 'w+')
            sample_file.close()
            # if os.path.isfile(hostdict):
            #     sample_file = open('/var/lib/syslog-ng/inside_condition.txt', 'w+')
            #     sample_file.close()
            #     os.remove(hostdict)

        except:
            return False

        self.logger.debug(f'hostip file')
        return True
