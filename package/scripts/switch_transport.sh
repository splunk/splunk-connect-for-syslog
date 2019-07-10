#!/bin/bash
#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause

#  Script to change all filters to use selected transport (UF, HEC, or kafka).
#  If one or more filters uses a transport different from all the others, they will need to be
#      managed by hand.  Unpredictable results can occur if the script is used and
#      individual filters are not checked for correctness.

case $SPLUNK_CONNECT_METHOD in
   hec)
      echo "Switching transport method for all filters to HEC"
      sed '/^# / {/#--HEC--/ s/^#/ /}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed '/^#/! {/#--KAFKA--/ s/^ /#/}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed '/^#/! {/#--UF--/ s/^ /#/}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed 's~__SPLUNK_HEC_URL__~"'"$SPLUNK_HEC_URL"'"~' -i /opt/syslog-ng/etc/syslog-ng.conf
      sed 's/__SPLUNK_HEC_TOKEN__/'"$SPLUNK_HEC_TOKEN"'/' -i /opt/syslog-ng/etc/syslog-ng.conf
      ;;
   kafka)
      echo "Switching transport method for all filters to Kafka"
      sed '/^# / {/#--KAFKA--/ s/^#/ /}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed '/^#/! {/#--HEC--/ s/^ /#/}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed '/^#/! {/#--UF--/ s/^ /#/}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      ;;
   UF)
      echo "Switching transport method for all filters to filesystem/UF"
      sed '/^# / {/#--UF--/ s/^#/ /}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed '/^#/! {/#--HEC--/ s/^ /#/}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      sed '/^#/! {/#--KAFKA--/ s/^ /#/}' -i /opt/syslog-ng/etc/conf.d/*.conf;
      ;;
   *)
      echo "Usage: $0 hec|kafka|UF"
      ;;
esac
