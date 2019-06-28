#!/usr/bin/dumb-init /bin/sh

#Run syslog
mkdir /opt/syslog-ng/var
rm /opt/syslog-ng/var/syslog-ng.ctl
/opt/syslog-ng/sbin/switch_transport.sh hec
/opt/syslog-ng/sbin/syslog-ng --process-mode=background
/opt/syslog-ng/sbin/splunkmetrics.sh 
