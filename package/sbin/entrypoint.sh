#!/opt/rh/rh-python36/root/usr/bin/dumb-init /bin/bash
#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause
#Run syslog
mkdir /opt/syslog-ng/var
rm /opt/syslog-ng/var/syslog-ng.ctl || true
/opt/syslog-ng/sbin/switch_transport.sh
/opt/syslog-ng/sbin/syslog-ng --process-mode=background
/opt/syslog-ng/sbin/splunkmetrics.sh 
