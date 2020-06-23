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

mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context
for file in /opt/syslog-ng/etc/conf.d/local/context/*.example ; do cp --verbose -n $file ${file%.example}; done

# splunk_index.csv updates
# Remove comment headers from existing config
touch /opt/syslog-ng/etc/conf.d/local/context/splunk_metadata.csv
if [ -f /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv ]; then
    LEGACY_SPLUNK_INDEX_FILE=/opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv
fi
# Add new entries
temp_file=$(mktemp)
awk '{print $0}' ${LEGACY_SPLUNK_INDEX_FILE} /opt/syslog-ng/etc/conf.d/local/context/splunk_metadata.csv /opt/syslog-ng/etc/context_templates/splunk_metadata.csv.example | grep -v '^#' | sort -b -t ',' -k1,2 -u  > $temp_file
cp -f $temp_file /opt/syslog-ng/etc/conf.d/local/context/splunk_metadata.csv
# We don't need this file any longer
rm -f /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv.example || true 
if [ -f /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv ]; then
    cp -f /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv /opt/syslog-ng/etc/conf.d/local/context/splunk_index.deprecated
    rm /opt/syslog-ng/etc/conf.d/local/context/splunk_index.csv
fi
cp --verbose -R -f /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/
mkdir -p /opt/syslog-ng/var/log

# Test HEC Connectivity
if [ "$SC4S_DEST_SPLUNK_HEC_GLOBAL" != "no" ]
then
  HEC=$(echo '{{- getenv "SPLUNK_HEC_URL" | strings.ReplaceAll "/services/collector" "" | strings.ReplaceAll "/event" "" | regexp.ReplaceLiteral "[, ]+" "/services/collector/event " }}/services/collector/event' | gomplate | cut -d' ' -f 1)
  SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX=$(cat /opt/syslog-ng/etc/conf.d/local/context/splunk_metadata.csv | grep ',index,' | grep sc4s_events | cut -d, -f 3)
  export SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX
  if curl -s -S -k "${HEC}?/index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX}" -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "SC4S:PROBE"}' 2>&1 | grep -v '{"text":"Success","code":0}'
  then
    echo -e "SC4S_ENV_CHECK_HEC: Invalid Splunk HEC URL, invalid token, or other HEC connectivity issue.\nStartup will continue to prevent data loss if this is a transient failure."
  else
    echo -e "\nSC4S_ENV_CHECK_HEC: Splunk HEC connection test successful; checking indexes...\n"
    cat /opt/syslog-ng/etc/conf.d/local/context/splunk_metadata.csv  | grep -v sc4s_metrics | grep ',index,' | cut -d, -f 3 | sort -u | while read index ; do export index; echo -e "SC4S_ENV_CHECK_INDEX: Checking $index" $(curl -s -S -k "${HEC}?index=${index}" -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "SC4S:PROBE"}') ; done
  fi
fi

# Run gomplate to create config from templates if the command errors this is fatal
# Stop the container. Errors in this step should only happen with user provided 
# Templates
if ! gomplate $(find . -name *.tmpl | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=etc/go_templates/; then
  echo "Error in Gomplate template; unable to continue, exiting..."
  exit 800
fi
# Setup SNMPD 
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
   echo "syslog-ng failed to start; PID $pid is not running, exiting..."
   if [ "${SC4S_DEBUG_CONTAINER}" != "yes" ]
   then
    exit $(wait ${pid})
  else
    tail -f /dev/null
  fi
   # Do something knowing the pid exists, i.e. the process with $PID is running
fi

# Wait forever
if [[ $@ != *"-s"* ]]; then
  while true
  do
    tail -f /dev/null & wait ${!}
  done
fi
