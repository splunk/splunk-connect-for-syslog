# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility
import sys
import traceback
import re

try:
    import syslogng
except:
    pass

regex = r"\"([^\"]+)\"=\"([^\"]+)\""

# test_str = "\"apMac\"=\"54:EC:2F:35:99:50\",\"radio\"=\"11g/n\",\"fromChannel\"=\"1\",\"toChannel\"=\"6\",\"apName\"=\"65-xx-xx-05labo.example.com\",\"fwVersion\"=\"5.2.2.0.1016\",\"model\"=\"R610\",\"zoneUUID\"=\"a7caf05c-3af6-4015-a715-5fc2aa0c16cf\",\"zoneName\"=\"zzz\",\"timeZone\"=\"CET-1CEST,M3.4.0/01:00,M10.5.0/01:00\",\"apLocation\"=\"\",\"apGps\"=\"\",\"apIpAddress\"=\"10.1.1.1\",\"apIpv6Address\"=\"\",\"apGroupUUID\"=\"34af29ac-1adb-4300-b851-d42b6ac555c3\",\"domainId\"=\"8b2081d5-9662-40d9-a3db-2a3cf4dde3f7\",\"serialNumber\"=\"401949001011\",\"domainName\"=\"Administration Domain\",\"idealEventVersion\"=\"3.5.1\",\"apDescription\"=\"\""

# matches = re.finditer(regex, test_str, re.MULTILINE)

# for matchNum, match in enumerate(matches, start=1):

#     print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))

#     for groupNum in range(0, len(match.groups())):
#         groupNum = groupNum + 1

#         print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))


class kvqf_parse(object):
    def init(self, options):
        self.logger = syslogng.Logger()
        return True

    def deinit(self):
        self.db.close()

    def parse(self, log_message):
        try:
            matches = re.finditer(
                regex, log_message[".tmp.pairs"].decode("utf-8"), re.MULTILINE
            )
            for matchNum, match in enumerate(matches, start=1):
                k = match.groups()[0]
                v = match.groups()[1]
                log_message[f".values.{k}"] = v
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.logger.debug("".join("!! " + line for line in lines))
            return False
        self.logger.debug(f"kvqf_parse.parse complete")
        return True
