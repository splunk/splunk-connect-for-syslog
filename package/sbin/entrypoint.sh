#!/usr/bin/env bash
function join_by { local d=$1; shift; local f=$1; shift; printf %s "$f" "${@/#/$d}"; }

export PYTHONPATH="/etc/syslog-ng/python:/usr/local/lib/python3.8/site-packages"

# These path variables allow for a single entrypoint script to be utilized for both Container and BYOE runtimes
export SC4S_LISTEN_DEFAULT_TCP_PORT=${SC4S_LISTEN_DEFAULT_TCP_PORT:=514}
export SC4S_LISTEN_DEFAULT_UDP_PORT=${SC4S_LISTEN_DEFAULT_UDP_PORT:=514}
export SC4S_LISTEN_DEFAULT_TLS_PORT=${SC4S_LISTEN_DEFAULT_TLS_PORT:=6514}
export SC4S_LISTEN_DEFAULT_RFC5426_PORT=${SC4S_LISTEN_DEFAULT_RFC5426_PORT:=601}
export SC4S_LISTEN_DEFAULT_RFC6587_PORT=${SC4S_LISTEN_DEFAULT_RFC6587_PORT:=601}
export SC4S_LISTEN_DEFAULT_RFC5425_PORT=${SC4S_LISTEN_DEFAULT_RFC5425_PORT:=5425}

export SC4S_DEFAULT_TIMEZONE=${SC4S_DEFAULT_TIMEZONE:=GMT}
export SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL_SECONDS=${SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL_SECONDS:=2}
export SC4S_DEST_SPLUNK_INDEXED_FIELDS=${SC4S_DEST_SPLUNK_INDEXED_FIELDS:=facility,container,loghost,destport,fromhostip,proto}

export SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX=${SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX:=fgt}

if [ -n "${SPLUNK_HEC_URL}" ]; then export SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$SPLUNK_HEC_URL; fi
if [ -n "${SPLUNK_HEC_TOKEN}" ]; then export SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=$SPLUNK_HEC_TOKEN; fi
if [ -n "${SC4S_DEST_SPLUNK_HEC_TLS_VERIFY}" ]; then export SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=$SC4S_DEST_SPLUNK_HEC_TLS_VERIFY; fi

export SC4S_ETC=${SC4S_ETC:=/etc/syslog-ng}
export SC4S_TLS=${SC4S_TLS:=/etc/syslog-ng/tls}
export SC4S_VAR=${SC4S_VAR:=/var/lib/syslog-ng}
export SC4S_BIN=${SC4S_BIN:=/usr/bin}
export SC4S_SBIN=${SC4S_SBIN:=/usr/sbin}

# The follwoing will be addressed in a future release
# source scl_source enable rh-python36

# The MICROFOCUS_ARCSIGHT destination is currently deprecated
# The unique port environment variables associated with MICROFOCUS_ARCSIGHT will be renamed to
# match the current CEF destination
# This block will be removed when the MICROFOCUS_ARCSIGHT destination is removed in version 2.0
if [ -n "${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_UDP_PORT}" ]; then export SC4S_LISTEN_CEF_UDP_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_UDP_PORT; fi
if [ -n "${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TCP_PORT}" ]; then export SC4S_LISTEN_CEF_TCP_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TCP_PORT; fi
if [ -n "${SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TLS_PORT}" ]; then export SC4S_LISTEN_CEF_TLS_PORT=$SC4S_LISTEN_MICROFOCUS_ARCSIGHT_TLS_PORT; fi
if [ -n "${SC4S_ARCHIVE_MICROFOCUS_ARCSIGHT}" ]; then export SC4S_ARCHIVE_CEF=$SC4S_ARCHIVE_MICROFOCUS_ARCSIGHT; fi
if [ -n "${SC4S_DEST_MICROFOCUS_ARCSIGHT_HEC}" ]; then export SC4S_DEST_CEF_HEC=$SC4S_DEST_MICROFOCUS_ARCSIGHT_HEC; fi

# The CISCO_ASA_LEGACY destination is currently deprecated
# The unique port environment variables associated with CISCO_ASA_LEGACY will be renamed to
# match the current CISCO_ASA destination
# This block will be removed when the CISCO_ASA_LEGACY destination is removed in version 2.0
if [ -n "${SC4S_LISTEN_CISCO_ASA_LEGACY_UDP_PORT}" ]; then export SC4S_LISTEN_CISCO_ASA_UDP_PORT=$SC4S_LISTEN_CISCO_ASA_LEGACY_UDP_PORT; fi
if [ -n "${SC4S_LISTEN_CISCO_ASA_LEGACY_TCP_PORT}" ]; then export SC4S_LISTEN_CISCO_ASA_TCP_PORT=$SC4S_LISTEN_CISCO_ASA_LEGACY_TCP_PORT; fi
if [ -n "${SC4S_LISTEN_CISCO_ASA_LEGACY_TLS_PORT}" ]; then export SC4S_LISTEN_CISCO_ASA_TLS_PORT=$SC4S_LISTEN_CISCO_ASA_LEGACY_TLS_PORT; fi
if [ -n "${SC4S_ARCHIVE_CISCO_ASA_LEGACY}" ]; then export SC4S_ARCHIVE_CISCO_ASA=$SC4S_ARCHIVE_CISCO_ASA_LEGACY; fi
if [ -n "${SC4S_DEST_CISCO_ASA_LEGACY_HEC}" ]; then export SC4S_DEST_CISCO_ASA_HEC=$SC4S_DEST_CISCO_ASA_LEGACY_HEC; fi

export SC4S_LISTEN_CISCO_IOS_TCP_PORT=$(join_by , $SC4S_LISTEN_CISCO_APIC_TCP_PORT $SC4S_LISTEN_CISCO_NX_OS_TCP_PORT $SC4S_LISTEN_CISCO_IOS_TCP_PORT)
[ -z "$SC4S_LISTEN_CISCO_IOS_TCP_PORT" ] && unset SC4S_LISTEN_CISCO_IOS_TCP_PORT
export SC4S_LISTEN_CISCO_IOS_UDP_PORT=$(join_by , $SC4S_LISTEN_CISCO_APIC_UDP_PORT $SC4S_LISTEN_CISCO_NX_OS_UDP_PORT $SC4S_LISTEN_CISCO_IOS_UDP_PORT)
[ -z "$SC4S_LISTEN_CISCO_IOS_UDP_PORT" ] && unset SC4S_LISTEN_CISCO_IOS_UDP_PORT

# The unique port environment variables associated with SC4S_LISTEN_<VENDOR_PRODUCT>_6587_PORT will be renamed to
# SC4S_LISTEN_<VENDOR_PRODUCT>_RFC6587_PORT to indicate compliance with the RFC.
# This compatibility block will be removed in version 2.0
for var in `env | awk -F "=" '{print $1}' | grep "_6587_"`; do
    export `echo $var | sed -n -e 's/_6587_PORT/_RFC6587_PORT/p'`=${!var}
done

export SC4S_DESTS_ALTERNATES=$(env | grep -v FILTERED_ALTERNATES | grep _ALTERNATES= | grep -v SC4S_DEST_GLOBAL_ALTERNATES | cut -d= -f2 | sort | uniq |  paste -s -d, -)
[ -z "$SC4S_DESTS_ALTERNATES" ] && unset SC4S_DESTS_ALTERNATES
export SC4S_DESTS_FILTERED_ALTERNATES=$(env | grep _FILTERED_ALTERNATES= | grep -v SC4S_DEST_GLOBAL_FILTERED_ALTERNATES | cut -d= -f2 | sort | uniq |  paste -s -d, -)
[ -z "$SC4S_DESTS_FILTERED_ALTERNATES" ] && unset SC4S_DESTS_FILTERED_ALTERNATES

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

if [ "$SC4S_MIGRATE_CONFIG" == "yes" ]
then
  if [ -d /opt/syslog-ng/var ]; then
    rmdir /var/lib/syslog-ng
    ln -s /opt/syslog-ng/var /var/lib/syslog-ng
  fi
  if [ -d /opt/syslog-ng/etc/conf.d/local ]; then
    mkdir -p $SC4S_VAR/log
    echo SC4S DEPRECATION WARNING: Please update the mount points in your sc4s.service file, as the internal container directory structure has changed.  See the relevant runtime documentation for the latest unit file recommendation. >>$SC4S_VAR/log/syslog-ng.out
    echo SC4S DEPRECATION WARNING: Please update the mount points in your sc4s.service file, as the internal container directory structure has changed.  See the relevant runtime documentation for the latest unit file recommendation.
    ln -s /opt/syslog-ng/etc/conf.d/local /etc/syslog-ng/conf.d/local
  fi
  if [ -d /opt/syslog-ng/tls ]; then
    ln -s /opt/syslog-ng/tls /etc/syslog-ng/tls
  fi
fi

mkdir -p $SC4S_VAR/log/
mkdir -p $SC4S_ETC/conf.d/local/context/
mkdir -p $SC4S_ETC/conf.d/merged/context/
mkdir -p $SC4S_ETC/conf.d/local/config/
mkdir -p $SC4S_ETC/local_config/

cp -f $SC4S_ETC/context_templates/* $SC4S_ETC/conf.d/local/context
if [ "$SC4S_RUNTIME_ENV" == "k8s" ]
then
  mkdir -p $SC4S_ETC/conf.d/configmap/context/
  mkdir -p $SC4S_ETC/conf.d/configmap/config/
  cp -f $SC4S_ETC/conf.d/configmap/context/splunk_metadata.csv $SC4S_ETC/conf.d/local/context/splunk_metadata.csv

else
  cp -R -f $SC4S_ETC/local_config/* $SC4S_ETC/conf.d/local/config/
fi
if [ "$TEST_SC4S_ACTIVATE_EXAMPLES" == "yes" ]
then  
  for file in $SC4S_ETC/conf.d/local/context/*.example ; do cp --verbose -n $file ${file%.example}; done
fi
for file in $SC4S_ETC/conf.d/local/context/*.example ; do touch ${file%.example}; done
touch $SC4S_ETC/conf.d/local/context/splunk_metadata.csv

if [ "$SC4S_SOURCE_TLS_SELFSIGNED" == "yes" ]
then  
  mkdir -p $SC4S_TLS || true
  KEY=${SC4S_TLS}/server.pem
  if [ ! -f "$KEY" ]; then
    openssl req -nodes -x509 -newkey rsa:4096 -keyout ${SC4S_TLS}/ca.key -out ${SC4S_TLS}/ca.crt -subj "/C=US/ST=ANY/L=ANY/O=SC4S Self Signer/OU=Splunk/CN=example.com"
    openssl req -nodes -newkey rsa:2048 -keyout ${SC4S_TLS}/server.key -out ${SC4S_TLS}/server.csr -subj "/C=US/ST=ANY/L=ANY/O=SC4S Self Signed Instance/OU=Splunk/CN=example.com"
    openssl x509 -req -in ${SC4S_TLS}/server.csr -CA ${SC4S_TLS}/ca.crt -CAkey ${SC4S_TLS}/ca.key -CAcreateserial -out ${SC4S_TLS}/server.pem
  fi
fi
if [ -f "${SC4S_TLS}/trusted.pem" ]
then
  cp ${SC4S_TLS}/trusted.pem /usr/share/pki/ca-trust-source/anchors/
  update-ca-trust
fi
if [ -f "${SC4S_TLS}/ca.crt" ]
then
  cp ${SC4S_TLS}/trusted.pem /usr/share/pki/ca-trust-source/anchors/
  update-ca-trust
fi
# Test HEC Connectivity
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$(echo $SC4S_DEST_SPLUNK_HEC_DEFAULT_URL | sed 's/\(https\{0,1\}\:\/\/[^\/, ]*\)[^, ]*/\1\/services\/collector\/event/g' | sed 's/,/ /g')
if [ "$SC4S_DEST_SPLUNK_HEC_GLOBAL" != "no" ]
then
  HEC=$(echo $SC4S_DEST_SPLUNK_HEC_DEFAULT_URL | cut -d' ' -f 1)
  if [ "${SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY}" == "no" ]; then export NO_VERIFY=-k ; fi
  SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX=$(grep -Po '(?<=^sc4s_fallback,index,).*' -m1 $SC4S_ETC/conf.d/local/context/splunk_metadata.csv )
  export SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX:=main}
  SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX=$(cat $SC4S_ETC/conf.d/local/context/splunk_metadata.csv | grep ',index,' | grep sc4s_events | cut -d, -f 3)
  export SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX:=main}

  if curl -s -S ${NO_VERIFY} "${HEC}?/index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX}" -H "Authorization: Splunk ${SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "sc4s:probe"}' 2>&1 | grep -v '{"text":"Success","code":0}'
  then
    echo -e "SC4S_ENV_CHECK_HEC: Invalid Splunk HEC URL, invalid token, or other HEC connectivity issue index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX}. sourcetype=sc4s:fallback\nStartup will continue to prevent data loss if this is a transient failure."
    echo ""
  else
    echo -e "SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX} for sourcetype=sc4s:fallback..."
    if curl -s -S ${NO_VERIFY} "${HEC}?/index=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX}" -H "Authorization: Splunk ${SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "sc4s:probe"}' 2>&1 | grep -v '{"text":"Success","code":0}'
      then
        echo -e "SC4S_ENV_CHECK_HEC: Invalid Splunk HEC URL, invalid token, or other HEC connectivity issue for index=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX}. sourcetype=sc4s:events \nStartup will continue to prevent data loss if this is a transient failure."
        echo ""
      else
        echo -e "SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX} for sourcetype=sc4s:events..."
      fi  
  fi
fi

# Create a workable variable with a list of simple log paths
export SOURCE_SIMPLE_SET=$(printenv | grep '^SC4S_LISTEN_SIMPLE_.*_PORT=.' | sed 's/^SC4S_LISTEN_SIMPLE_//;s/_..._PORT\=.*//;s/_[^_]*_PORT\=.*//' | sort | uniq |  xargs echo | sed 's/ /,/g' | tr '[:upper:]' '[:lower:]' )
export SOURCE_ALL_SET=$(printenv | grep '^SC4S_LISTEN_.*_PORT=.' | grep -v "disabled" | sed 's/^SC4S_LISTEN_//;s/_..._PORT\=.*//;s/_[^_]*_PORT\=.*//' | sort | uniq |  xargs echo | sed 's/ /,/g' | tr '[:lower:]' '[:upper:]' )

export DEST_ARCHIVE_PATTERN=$(printenv | grep ARC | grep yes | sed 's/SC4S_DEST_//' | sed 's/_ARCHIVE=yes//' | sort | uniq |  xargs echo | sed 's/ /|/g')
export DEST_HEC_PATTERN=$(printenv | grep ARC | grep yes | sed 's/SC4S_DEST_//' | sed 's/_HEC=yes//' | sort | uniq |  xargs echo | sed 's/ /|/g')

#gomplate templates are obsolete 
pushd $SC4S_ETC >/dev/null
#remove old gomplate examples
rm -f $SC4S_ETC/conf.d/local/config/app_parsers/syslog/app-nix_example.conf.tmpl || true
rm -f $SC4S_ETC/conf.d/local/config/log_paths/lp-example.conf || true
rm -f $SC4S_ETC/conf.d/local/config/log_paths/lp-example.conf.tmpl || true

if [[ -n $(find ./conf.d/local/ -name *.tmpl) ]]
then 
  echo Local log paths were found using the deprecated "gomplate" template format.  Please convert them using the new app-parser template example.
  find ./conf.d/local/ -name *.tmpl | sed -e 's/..conf.d/<SC4S config path>/'
  if [[ $(command -v gomplate) ]]
  then
    if ! gomplate $(find . -name "*.tmpl" | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=$SC4S_ETC/go_templates/
    then
      echo "Error in Gomplate template; unable to continue, exiting..."
      exit 800
    fi
  fi
fi
popd >/dev/null
syslog-ng --no-caps --preprocess-into=- | grep vendor_product | grep set | grep -v 'set(.\$' | sed 's/^ *//' | grep 'value("fields.sc4s_vendor_product"' | grep -v "\`vendor_product\`" | sed s/^set\(// | cut -d',' -f1 | sed 's/\"//g' >/tmp/keys
syslog-ng --no-caps --preprocess-into=- | grep 'meta_key(.' | sed 's/^ *meta_key(.//' | sed "s/')//" >>/tmp/keys
rm -f $SC4S_ETC/conf.d/local/context/splunk_metadata.csv.example >/dev/null || true
for fn in `cat /tmp/keys | sort | uniq`; do
    echo "${fn},index,setme" >>$SC4S_ETC/conf.d/local/context/splunk_metadata.csv.example
done

# OPTIONAL for BYOE:  Comment out SNMP stanza immediately below and launch snmptrapd directly from systemd
# Launch snmptrapd

if [ "$SC4S_SNMP_TRAP_COLLECT" == "yes" ]
then
/opt/net-snmp/sbin/snmptrapd -Lf $SC4S_VAR/log/snmptrapd.log
fi

echo syslog-ng checking config
echo sc4s version=$(cat $SC4S_ETC/VERSION)
echo sc4s version=$(cat $SC4S_ETC/VERSION) >>$SC4S_VAR/log/syslog-ng.out
$SC4S_SBIN/syslog-ng --no-caps $SC4S_CONTAINER_OPTS -s >>$SC4S_VAR/log/syslog-ng.out 2>$SC4S_VAR/log/syslog-ng.err

# Use gomplate to pick up default listening ports for health check
if command -v goss &> /dev/null
then
  echo starting goss
  goss -g $SC4S_ETC/goss.yaml serve -l 0.0.0.0:8080 --format json >/dev/null 2>/dev/null &
fi

# OPTIONAL for BYOE:  Comment out/remove all remaining lines and launch syslog-ng directly from systemd
if [ "${SC4S_DEBUG_CONTAINER}" == "yes" ]
then
  syslog-ng --no-caps --preprocess-into=/tmp/syslog-ng.conf
  printenv >/tmp/env_file
  export >/tmp/export_file
fi

syslog-ng -s --no-caps
if [ $? != 0 ]
then
  if [ "${SC4S_DEBUG_CONTAINER}" == "yes" ]
  then
    tail -f /dev/null
  else 
    exit $?
  fi
fi

while :
do
  echo starting syslog-ng
  $SC4S_SBIN/syslog-ng --no-caps $SC4S_CONTAINER_OPTS -F $@ &
  pid="$!"
  sleep 2
  if [ "${SC4S_DEBUG_CONTAINER}" == "yes" ]
  then
    echo "Container debug enabled; waiting forever. Errors will not cause container to stop..."
    tail -f /dev/null
  else
    if ! ps -p $pid > /dev/null
    then
      echo "syslog-ng failed to start; exiting..."
    fi
    wait ${pid}
    if [ $? == 147 ]
    then 
      exit $?    
    else
      echo "Handling exit $? and restarting"    
    fi
  fi
done