#!/usr/bin/env bash

# The follwoing will be addressed in a future release
# source scl_source enable rh-python36

# The MICROFOCUS_ARCSIGHT unique port environment variables are currently deprecated
# This will be removed when the MICROFOCUS_ARCSIGHT unique port environment variables are removed in version 2.0
if [ ${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_UDP_PORT} ]; then export SC4S_LISTEN_CEF_UDP_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_UDP_PORT; fi
if [ ${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TCP_PORT} ]; then export SC4S_LISTEN_CEF_TCP_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TCP_PORT; fi
if [ ${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TLS_PORT} ]; then export SC4S_LISTEN_CEF_TLS_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TLS_PORT; fi
if [ ${SC4S_ARCHIVE_MICROFOCUS_ARCSIGHT} ]; then export SC4S_ARCHIVE_CEF=$SC4S_ARCHIVE_MICROFOCUS_ARCSIGHT; fi
if [ ${SC4S_DEST_MICROFOCUS_ARCSIGHT_HEC} ]; then export SC4S_DEST_CEF_HEC=$SC4S_DEST_MICROFOCUS_ARCSIGHT_HEC; fi

cd /opt/syslog-ng

# SIGTERM-handler
term_handler() {
  if [ $pid -ne 0 ]; then
    echo Terminating
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

# SIGHUP-handler
hup_handler() {
  if [ $pid -ne 0 ]; then
    echo Reloading
    kill -SIGHUP "$pid"
  fi
}

trap 'kill ${!}; hup_handler' SIGHUP
trap 'kill ${!}; term_handler' SIGTERM


gomplate $(find . -name *.tmpl | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=etc/go_templates/

mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context/
for file in /opt/syslog-ng/etc/conf.d/local/context/*.example ; do cp --verbose -n $file ${file%.example}; done
cp --verbose -R /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/
mkdir -p /opt/syslog-ng/var/log

#Test HEC Connectivity
HEC=$(echo '{{- getenv "SPLUNK_HEC_URL" | strings.ReplaceAll "/services/collector" "" | strings.ReplaceAll "/event" "" | regexp.ReplaceLiteral "[, ]+" "/services/collector/event " }}/services/collector/event' | gomplate | cut -d' ' -f 1)
index=$(cat /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv  | grep sc4s_events | cut -d, -f 3)
if ! curl -k "${HEC}?/index=${index}" -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "SC4S:PROBE"}'
then
  echo SC4S_ENV_CHECK_HEC: Splunk unreachable startup will continue to prevent data loss if this is a transient failure
else
  echo SC4S_ENV_CHECK_INDEX: Splunk connection succesfull checking indexes
  cat /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv  | grep -v sc4s_metrics | cut -d, -f 3 | sort -u | while read index ; do export index; echo -e "\nSC4S_ENV_CHECK_INDEX: Checking $index" $(curl -s -S -k "${HEC}?index=${index}" -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "SC4S:PROBE"}') ; done
fi

#Setup SNMPD 
/opt/net-snmp/sbin/snmptrapd -Lf /opt/syslog-ng/var/log/snmptrapd.log

echo syslog-ng checking config
echo sc4s version=$(cat /VERSION)
echo sc4s version=$(cat /VERSION) >/opt/syslog-ng/var/log/syslog-ng.out
/opt/syslog-ng/sbin/syslog-ng -s >>/opt/syslog-ng/var/log/syslog-ng.out 2>/opt/syslog-ng/var/log/syslog-ng.err

echo syslog-ng starting
/opt/syslog-ng/bin/persist-tool add /opt/syslog-ng/etc/reset_persist -o /opt/syslog-ng/var

/opt/syslog-ng/sbin/syslog-ng $@ &
pid="$!"
sleep 5
if ! ps -p $pid > /dev/null
then
   echo "SC4S_ENV_CHECK_SYSLOG-NG failed to start $pid is not running"
   /opt/syslog-ng/sbin/syslog-ng -s
   if [ "${SC4S_DEBUG_CONTAINER}" == "yes" ]
   then
    exit $(wait ${pid})
  else
    tail -f /dev/null
  fi
   # Do something knowing the pid exists, i.e. the process with $PID is running
fi

# wait forever
if [[ $@ != *"-s"* ]]; then
  while true
  do
    tail -f /dev/null & wait ${!}
  done
fi
