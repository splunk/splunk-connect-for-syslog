#Splunk Connect for Syslog (SC4S) by Splunk, Inc.
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
ARG BRANCH=master
FROM splunk/scs:base-${BRANCH}

COPY --from=hairyhenderson/gomplate:v3.5.0 /gomplate /usr/local/bin/gomplate

COPY goss.yaml goss.yaml

COPY etc/syslog-ng.conf /opt/syslog-ng/etc/syslog-ng.conf
COPY etc/conf.d /opt/syslog-ng/etc/conf.d
COPY etc/go_templates /opt/syslog-ng/etc/go_templates
COPY etc/context_templates /opt/syslog-ng/etc/context_templates
COPY etc/local_config /opt/syslog-ng/etc/local_config
COPY reset_persist /opt/syslog-ng/etc/
COPY sbin/entrypoint.sh /

RUN mkdir -p /opt/syslog-ng/var/log/
COPY snmp/snmptrapd.conf /opt/net-snmp/etc/snmp/
COPY VERSION /

RUN  /opt/syslog-ng/sbin/syslog-ng -V

#USER [syslog]