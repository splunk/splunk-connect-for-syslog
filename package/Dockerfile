#Splunk Connect for Syslog (SC4S) by Splunk, Inc.
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Connect for Syslog (SC4S).
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#Splunk Syslog-NG Container Image
#
#To the extent possible under law, the person who associated CC0 with
#Splunk Connect for Syslog (SC4S) has waived all copyright and related or neighboring rights
#to Splunk Syslog-NG Container image.
#
#You should have received a copy of the CC0 legalcode along with this
#work.  If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
ARG SC4S_BASE_IMAGE=edge
FROM splunk/scs:${SC4S_BASE_IMAGE}


COPY package/etc/goss.yaml.tmpl /opt/syslog-ng/etc/goss.yaml.tmpl

COPY package/etc/syslog-ng.conf.tmpl /opt/syslog-ng/etc/syslog-ng.conf.tmpl
COPY package/etc/conf.d /opt/syslog-ng/etc/conf.d
COPY package/etc/go_templates /opt/syslog-ng/etc/go_templates
COPY package/etc/context_templates /opt/syslog-ng/etc/context_templates
COPY package/etc/local_config /opt/syslog-ng/etc/local_config
COPY package/sbin/entrypoint.sh /

RUN mkdir -p /opt/syslog-ng/var/log/
COPY package/snmp/snmptrapd.conf /opt/net-snmp/etc/snmp/
COPY package/VERSION /

RUN  /opt/syslog-ng/sbin/syslog-ng -V