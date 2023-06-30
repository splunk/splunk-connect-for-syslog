
import os

try:
    import syslogng
except:
    pass

hostdict = str("/var/lib/syslog-ng/hostip.sqlite")


class clear_name_cache(object):

    def parse(self, log_message):

        try:
            self.logger = syslogng.Logger()
            sample_file = open('/var/lib/syslog-ng/after_call.txt', 'w+')
            sample_file.close()
            if os.path.isfile('/var/lib/syslog-ng/after_call.txt'):
                sample_file = open('/var/lib/syslog-ng/check_file.txt', 'w+')
                sample_file.close()
            if os.path.isfile(hostdict):
                os.remove(hostdict)
        except:
            return False

        self.logger.debug(f'hostip file')
        return True
