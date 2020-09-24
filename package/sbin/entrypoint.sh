#!/usr/bin/env bash

# These path variables allow for a single entrypoint script to be utilized for both Container and BYOE runtimes
export SC4S_ETC=${SC4S_ETC:=/opt/syslog-ng/etc}
export SC4S_VAR=${SC4S_VAR:=/opt/syslog-ng/var}
export SC4S_BIN=${SC4S_BIN:=/opt/syslog-ng/bin}
export SC4S_SBIN=${SC4S_SBIN:=/opt/syslog-ng/sbin}
export SC4S_TLS=${SC4S_TLS:=/opt/syslog-ng/tls}

# The follwoing will be addressed in a future release
# source scl_source enable rh-python36

# The MICROFOCUS_ARCSIGHT destination is currently deprecated
# The unique port environment variables associated with MICROFOCUS_ARCSIGHT will be renamed to
# match the current CEF destination
# This block will be removed when the MICROFOCUS_ARCSIGHT destination is removed in version 2.0
if [ ${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_UDP_PORT} ]; then export SC4S_LISTEN_CEF_UDP_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_UDP_PORT; fi
if [ ${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TCP_PORT} ]; then export SC4S_LISTEN_CEF_TCP_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TCP_PORT; fi
if [ ${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TLS_PORT} ]; then export SC4S_LISTEN_CEF_TLS_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TLS_PORT; fi
if [ ${SC4S_ARCHIVE_MICROFOCUS_ARCSIGHT} ]; then export SC4S_ARCHIVE_CEF=$SC4S_ARCHIVE_MICROFOCUS_ARCSIGHT; fi
if [ ${SC4S_DEST_MICROFOCUS_ARCSIGHT_HEC} ]; then export SC4S_DEST_CEF_HEC=$SC4S_DEST_MICROFOCUS_ARCSIGHT_HEC; fi

# The CISCO_ASA_LEGACY destination is currently deprecated
# The unique port environment variables associated with CISCO_ASA_LEGACY will be renamed to
# match the current CISCO_ASA destination
# This block will be removed when the CISCO_ASA_LEGACY destination is removed in version 2.0
if [ ${SC4S_LISTEN_CISCO_ASA_LEGACY_UDP_PORT} ]; then export SC4S_LISTEN_CISCO_ASA_UDP_PORT=$SC4S_LISTEN_CISCO_ASA_LEGACY_UDP_PORT; fi
if [ ${SC4S_LISTEN_CISCO_ASA_LEGACY_TCP_PORT} ]; then export SC4S_LISTEN_CISCO_ASA_TCP_PORT=$SC4S_LISTEN_CISCO_ASA_LEGACY_TCP_PORT; fi
if [ ${SC4S_LISTEN_CISCO_ASA_LEGACY_TLS_PORT} ]; then export SC4S_LISTEN_CISCO_ASA_TLS_PORT=$SC4S_LISTEN_CISCO_ASA_LEGACY_TLS_PORT; fi
if [ ${SC4S_ARCHIVE_CISCO_ASA_LEGACY} ]; then export SC4S_ARCHIVE_CISCO_ASA=$SC4S_ARCHIVE_CISCO_ASA_LEGACY; fi
if [ ${SC4S_DEST_CISCO_ASA_LEGACY_HEC} ]; then export SC4S_DEST_CISCO_ASA_HEC=$SC4S_DEST_CISCO_ASA_LEGACY_HEC; fi

cd $SC4S_ETC
mkdir -p local_config

# SIGTERM-handler
term_handler() {
# SIGTERM on valid PID; return exit code 0 (clean exit)
  if [ $pid -ne 0 ]; then
    echo Terminating syslog-ng...
    kill -SIGTERM ${pid}
    wait ${pid}
    exit $?
  fi
# 128 + 15 -- SIGTERM on non-existent process (will cause service failure)
  exit 143
}

# SIGHUP-handler
hup_handler() {
  if [ $pid -ne 0 ]; then
    echo Reloading syslog-ng...
    kill -SIGHUP ${pid}
  fi
}

# SIGQUIT-handler
quit_handler() {
  if [ $pid -ne 0 ]; then
    echo Quitting syslog-ng...
    kill -SIGQUIT ${pid}
    wait ${pid}
  fi
}

trap 'kill ${!}; hup_handler' SIGHUP
trap 'kill ${!}; term_handler' SIGTERM
trap 'kill ${!}; quit_handler' SIGQUIT

mkdir -p $SC4S_ETC/conf.d/local/context/
mkdir -p $SC4S_ETC/conf.d/merged/context/
mkdir -p $SC4S_ETC/conf.d/local/config/



cp $SC4S_ETC/context_templates/* $SC4S_ETC/conf.d/local/context
for file in $SC4S_ETC/conf.d/local/context/*.example ; do cp --verbose -n $file ${file%.example}; done
if [ "$SC4S_RUNTIME_ENV" == "k8s" ]
then
  mkdir -p $SC4S_ETC/conf.d/configmap/context/
  mkdir -p $SC4S_ETC/conf.d/configmap/config/
  # Add new entries
  temp_file=$(mktemp)
  awk '{print $0}' $SC4S_ETC/conf.d/configmap/context/splunk_metadata.csv $SC4S_ETC/context_templates/splunk_metadata.csv.example | grep -v '^#' | sort -b -t ',' -k1,2 -u  > $temp_file
  cp -f $temp_file $SC4S_ETC/conf.d/merged/context/splunk_metadata.csv

else
  # splunk_index.csv updates
  # Remove comment headers from existing config
  touch $SC4S_ETC/conf.d/local/context/splunk_metadata.csv
  if [ -f $SC4S_ETC/conf.d/local/context/splunk_index.csv ]; then
      LEGACY_SPLUNK_INDEX_FILE=$SC4S_ETC/conf.d/local/context/splunk_index.csv
  fi

  # Add new entries
  temp_file=$(mktemp)
  awk '{print $0}' ${LEGACY_SPLUNK_INDEX_FILE} $SC4S_ETC/conf.d/local/context/splunk_metadata.csv $SC4S_ETC/context_templates/splunk_metadata.csv.example | grep -v '^#' | sort -b -t ',' -k1,2 -u  > $temp_file
  cp -f $temp_file $SC4S_ETC/conf.d/merged/context/splunk_metadata.csv
  # We don't need this file any longer
  rm -f $SC4S_ETC/conf.d/local/context/splunk_index.csv.example || true
  if [ -f $SC4S_ETC/conf.d/local/context/splunk_index.csv ]; then
      cp -f $SC4S_ETC/conf.d/local/context/splunk_index.csv $SC4S_ETC/conf.d/local/context/splunk_index.deprecated
      rm $SC4S_ETC/conf.d/local/context/splunk_index.csv
  fi
  cp --verbose -R -f $SC4S_ETC/local_config/* $SC4S_ETC/conf.d/local/config/
fi
mkdir -p $SC4S_VAR/log

# Test HEC Connectivity
if [ "$SC4S_DEST_SPLUNK_HEC_GLOBAL" != "no" ]
then
  HEC=$(echo '{{- getenv "SPLUNK_HEC_URL" | strings.ReplaceAll "/services/collector" "" | strings.ReplaceAll "/event" "" | regexp.ReplaceLiteral "[, ]+" "/services/collector/event " }}/services/collector/event' | gomplate | cut -d' ' -f 1)
  NO_VERIFY=$(echo '{{- if not (conv.ToBool (getenv "SC4S_DEST_SPLUNK_HEC_TLS_VERIFY" "yes")) }}-k{{- end}}' | gomplate)
  SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX=$(cat $SC4S_ETC/conf.d/local/context/splunk_metadata.csv | grep ',index,' | grep sc4s_events | cut -d, -f 3)
  export SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX
  if curl -s -S ${NO_VERIFY} "${HEC}?/index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX}" -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "SC4S:PROBE"}' 2>&1 | grep -v '{"text":"Success","code":0}'
  then
    echo -e "SC4S_ENV_CHECK_HEC: Invalid Splunk HEC URL, invalid token, or other HEC connectivity issue.\nStartup will continue to prevent data loss if this is a transient failure."
  else
    echo -e "\nSC4S_ENV_CHECK_HEC: Splunk HEC connection test successful; checking indexes...\n"
    cat $SC4S_ETC/conf.d/local/context/splunk_metadata.csv  | grep -v sc4s_metrics | grep ',index,' | cut -d, -f 3 | sort -u | while read index ; do export index; echo -e "SC4S_ENV_CHECK_INDEX: Checking $index" $(curl -s -S -k "${HEC}?index=${index}" -H "Authorization: Splunk ${SPLUNK_HEC_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "SC4S:PROBE"}') ; done
  fi
fi

# Run gomplate to create config from templates if the command errors this is fatal
# Stop the container. Errors in this step should only happen with user provided
# Templates
if ! gomplate $(find . -name "*.tmpl" | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=$SC4S_ETC/go_templates/; then
  echo "Error in Gomplate template; unable to continue, exiting..."
  exit 800
fi

# OPTIONAL for BYOE:  Comment out SNMP stanza immediately below and launch snmptrapd directly from systemd
# Launch snmptrapd

if [ "$SC4S_SNMP_TRAP_COLLECT" == "yes" ]
then
/opt/net-snmp/sbin/snmptrapd -Lf $SC4S_VAR/log/snmptrapd.log
fi

echo syslog-ng checking config
echo sc4s version=$(cat $SC4S_ETC/VERSION)
echo sc4s version=$(cat $SC4S_ETC/VERSION) >$SC4S_VAR/log/syslog-ng.out
$SC4S_SBIN/syslog-ng -s >>$SC4S_VAR/log/syslog-ng.out 2>$SC4S_VAR/log/syslog-ng.err

# Use gomplate to pick up default listening ports for health check
if command -v goss &> /dev/null
then
  echo starting goss
  gomplate --file $SC4S_ETC/goss.yaml.tmpl --out $SC4S_ETC/goss.yaml
  goss -g $SC4S_ETC/goss.yaml serve --format json >/dev/null 2>/dev/null &
fi

# OPTIONAL for BYOE:  Comment out/remove all remaining lines and launch syslog-ng directly from systemd

echo starting syslog-ng
$SC4S_SBIN/syslog-ng -F $@ &
pid="$!"
sleep 2
if ! ps -p $pid > /dev/null
then
   echo "syslog-ng failed to start; exiting..."
   if [ "${SC4S_DEBUG_CONTAINER}" != "yes" ]
   then
     wait ${pid}
     exit $?
  else
    tail -f /dev/null
  fi
   # Do something knowing the pid exists, i.e. the process with $PID is running
fi

# Wait forever
wait ${pid}
exit $?
