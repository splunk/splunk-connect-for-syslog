#!/opt/rh/rh-python36/root/usr/bin/dumb-init /bin/bash

#Run syslog
mkdir /opt/syslog-ng/var
rm /opt/syslog-ng/var/syslog-ng.ctl || true
/opt/syslog-ng/sbin/switch_transport.sh
/opt/syslog-ng/sbin/syslog-ng --process-mode=background
/opt/syslog-ng/sbin/splunkmetrics.sh 
