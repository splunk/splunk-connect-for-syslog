#!/usr/bin/env bash
function join_by { local d=$1; shift; local f=$1; shift; printf %s "$f" "${@/#/$d}"; }
. /var/lib/python-venv/bin/activate
export PYTHONPATH=/etc/syslog-ng/pylib

python3 /etc/syslog-ng/pylib/parser_source_cache.py

export SC4S_LISTEN_STATUS_PORT=${SC4S_LISTEN_STATUS_PORT:=8080}

# These path variables allow for a single entrypoint script to be utilized for both Container and BYOE runtimes
export SC4S_LISTEN_DEFAULT_TCP_PORT=${SC4S_LISTEN_DEFAULT_TCP_PORT:=514}
export SC4S_LISTEN_DEFAULT_UDP_PORT=${SC4S_LISTEN_DEFAULT_UDP_PORT:=514}
export SC4S_LISTEN_DEFAULT_TLS_PORT=${SC4S_LISTEN_DEFAULT_TLS_PORT:=6514}
export SC4S_LISTEN_DEFAULT_RFC5426_PORT=${SC4S_LISTEN_DEFAULT_RFC5426_PORT:=601}
export SC4S_LISTEN_DEFAULT_RFC6587_PORT=${SC4S_LISTEN_DEFAULT_RFC6587_PORT:=601}
export SC4S_LISTEN_DEFAULT_RFC5425_PORT=${SC4S_LISTEN_DEFAULT_RFC5425_PORT:=5425}
export SC4S_CLEAR_NAME_CACHE=${SC4S_CLEAR_NAME_CACHE:=no}

export SC4S_DEFAULT_TIMEZONE=${SC4S_DEFAULT_TIMEZONE:=GMT}
export SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL_SECONDS=${SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL_SECONDS:=2}
export SC4S_DEST_SPLUNK_INDEXED_FIELDS=${SC4S_DEST_SPLUNK_INDEXED_FIELDS:=r_unixtime,facility,container,loghost,destport,fromhostip,proto,severity}

export SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX=${SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX:=fgt}

if [ -n "${SPLUNK_HEC_URL}" ]; then export SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$SPLUNK_HEC_URL; fi
if [ -n "${SPLUNK_HEC_TOKEN}" ]; then export SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=$SPLUNK_HEC_TOKEN; fi
if [ -n "${SC4S_DEST_SPLUNK_HEC_TLS_VERIFY}" ]; then export SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=$SC4S_DEST_SPLUNK_HEC_TLS_VERIFY; fi

export SC4S_ETC=${SC4S_ETC:=/etc/syslog-ng}
export SC4S_TLS=${SC4S_TLS:=/etc/syslog-ng/tls}
export SC4S_VAR=${SC4S_VAR:=/var/lib/syslog-ng}
export SC4S_BIN=${SC4S_BIN:=/usr/bin}
export SC4S_SBIN=${SC4S_SBIN:=/usr/sbin}

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

mkdir -p $SC4S_VAR/log/
mkdir -p $SC4S_ETC/conf.d/local/context/
mkdir -p $SC4S_ETC/conf.d/merged/context/
mkdir -p $SC4S_ETC/conf.d/local/config/
mkdir -p $SC4S_ETC/conf.d/local/config/app_parsers/
mkdir -p $SC4S_ETC/local_config/
mkdir -p $SC4S_ETC/addons/

# copy all files in context_templates to conf.d/local/context
cp -f $SC4S_ETC/context_templates/* $SC4S_ETC/conf.d/local/context

# check if runtime environment is k8s
if [ "$SC4S_RUNTIME_ENV" == "k8s" ]
then
  # create directories if they don't exist
  mkdir -p $SC4S_ETC/conf.d/configmap/context/
  mkdir -p $SC4S_ETC/conf.d/configmap/config/app_parsers/
  mkdir -p $SC4S_ETC/conf.d/configmap/addons/

  # copy all files in configmap/context to conf.d/local/context

  cp -R -f $SC4S_ETC/conf.d/configmap/* $SC4S_ETC/conf.d/local/
  #cp -f $SC4S_ETC/conf.d/configmap/context/splunk_metadata.csv $SC4S_ETC/conf.d/local/context/splunk_metadata.csv
  #cp -R -f $SC4S_ETC/conf.d/configmap/config/* $SC4S_ETC/conf.d/local/config/app_parsers/
  if [[ -f $SC4S_ETC/conf.d/configmap/addons/config.yaml ]]; then
    cp $SC4S_ETC/conf.d/configmap/addons/config.yaml $SC4S_ETC/config.yaml
  fi
else
  # copy all files in local_config to conf.d/local/config
  cp -R -f $SC4S_ETC/local_config/* $SC4S_ETC/conf.d/local/config/
fi

if [[ -f $SC4S_ETC/syslog-ng.conf.jinja ]]; then
  python3 -m config_generator --config=$SC4S_ETC/config.yaml > $SC4S_ETC/syslog-ng.conf
fi

if [ "$TEST_SC4S_ACTIVATE_EXAMPLES" == "yes" ]
then
  for file in $SC4S_ETC/conf.d/local/context/*.example ; do cp --verbose -n $file ${file%.example}; done
  cp -f $SC4S_ETC/test_parsers/* $SC4S_ETC/conf.d/local/config/app_parsers/
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
# if [ -f "${SC4S_TLS}/trusted.pem" ]
# then
#   cp ${SC4S_TLS}/trusted.pem /usr/share/pki/ca-trust-source/anchors/
#   update-ca-trust
# fi
# if [ -f "${SC4S_TLS}/ca.crt" ]
# then
#   cp ${SC4S_TLS}/trusted.pem /usr/share/pki/ca-trust-source/anchors/
#   update-ca-trust
# fi 

# Check Linux distribution if its alpine
if grep -q 'alpine' /etc/os-release; then
  IS_ALPINE=true
else
  IS_ALPINE=false
fi
if [ "$IS_ALPINE" = true ]; then
  if [ -f "${SC4S_TLS}/trusted.pem" ]
  then
    cp ${SC4S_TLS}/trusted.pem /usr/local/share/ca-certificates/trusted.crt
    update-ca-certificates
  fi
  if [ -f "${SC4S_TLS}/ca.crt" ]
  then
    cp ${SC4S_TLS}/ca.crt /usr/local/share/ca-certificates/
    update-ca-certificates
  fi
else
  # if we fallback to ubi
  if [ -f "${SC4S_TLS}/trusted.pem" ]
  then
    cp ${SC4S_TLS}/trusted.pem /usr/share/pki/ca-trust-source/anchors/
    update-ca-trust
  fi
  if [ -f "${SC4S_TLS}/ca.crt" ]
  then
    cp ${SC4S_TLS}/ca.crt /usr/share/pki/ca-trust-source/anchors/
    update-ca-trust
  fi
fi
# Test HEC Connectivity
SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$(echo $SC4S_DEST_SPLUNK_HEC_DEFAULT_URL | sed 's/\(https\{0,1\}\:\/\/[^\/, ]*\)[^, ]*/\1\/services\/collector\/event/g' | sed 's/,/ /g')
if [ "$SC4S_DEST_SPLUNK_HEC_GLOBAL" != "no" ]
then
  HEC=$(echo $SC4S_DEST_SPLUNK_HEC_DEFAULT_URL | cut -d' ' -f 1)
  if [ "${SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY}" == "no" ]; then export NO_VERIFY=-k ; fi
  SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX=$(grep -Po '(?<=^splunk_sc4s_fallback,index,).*' -m1 $SC4S_ETC/conf.d/local/context/splunk_metadata.csv )
  export SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX:=main}
  SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX=$(cat $SC4S_ETC/conf.d/local/context/splunk_metadata.csv | grep ',index,' | grep sc4s_events | cut -d, -f 3)
  export SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX:=main}

  if curl -s -S ${NO_VERIFY} "${HEC}?/index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX}" -H "Authorization: Splunk ${SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "sc4s:probe"}' 2>&1 | grep -v '{"text":"Success"'
  then
    echo -e "SC4S_ENV_CHECK_HEC: Invalid Splunk HEC URL, invalid token, or other HEC connectivity issue index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX}. sourcetype=sc4s:fallback\nStartup will continue to prevent data loss if this is a transient failure."
    echo ""
  else
    echo -e "SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=${SC4S_DEST_SPLUNK_HEC_FALLBACK_INDEX} for sourcetype=sc4s:fallback..."
    if curl -s -S ${NO_VERIFY} "${HEC}?/index=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX}" -H "Authorization: Splunk ${SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN}" -d '{"event": "HEC TEST EVENT", "sourcetype": "sc4s:probe"}' 2>&1 | grep -v '{"text":"Success"'
      then
        echo -e "SC4S_ENV_CHECK_HEC: Invalid Splunk HEC URL, invalid token, or other HEC connectivity issue for index=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX}. sourcetype=sc4s:events \nStartup will continue to prevent data loss if this is a transient failure."
        echo ""
      else
        echo -e "SC4S_ENV_CHECK_HEC: Splunk HEC connection test successful to index=${SC4S_DEST_SPLUNK_HEC_EVENTS_INDEX} for sourcetype=sc4s:events..."
      fi
  fi
fi

if [ "${SC4S_CLEAR_NAME_CACHE}" == "yes" ] || [ "${SC4S_CLEAR_NAME_CACHE}" == "1" ]
then 
  rm -f $SC4S_VAR/hostip.sqlite
  echo "hostip.sqlite file deleted at $SC4S_VAR"
fi

# Create a workable variable with a list of simple log paths
export SOURCE_SIMPLE_SET=$(printenv | grep '^SC4S_LISTEN_SIMPLE_.*_PORT=.' | sed 's/^SC4S_LISTEN_SIMPLE_//;s/_..._PORT\=.*//;s/_[^_]*_PORT\=.*//' | sort | uniq |  xargs echo | sed 's/ /,/g' | tr '[:upper:]' '[:lower:]' )
export SOURCE_ALL_SET=$(printenv | grep '^SC4S_LISTEN_.*_PORT=.' | grep -v "disabled" | sed 's/^SC4S_LISTEN_//;s/_..._PORT\=.*//;s/_[^_]*_PORT\=.*//' | sort | uniq |  xargs echo | sed 's/ /,/g' | tr '[:lower:]' '[:upper:]' )

python3 /source_ports_validator.py

syslog-ng --no-caps --preprocess-into=- | grep vendor_product | grep set | grep -v 'set(.\$' | sed 's/^ *//' | grep 'value("fields.sc4s_vendor_product"' | grep -v "\`vendor_product\`" | sed s/^set\(// | cut -d',' -f1 | sed 's/\"//g' >/tmp/keys
syslog-ng --no-caps --preprocess-into=- | grep 'meta_key(.' | sed 's/^ *meta_key(.//' | sed "s/')//" >>/tmp/keys
rm -f $SC4S_ETC/conf.d/local/context/splunk_metadata.csv.example >/dev/null || true
for fn in `cat /tmp/keys | sort | uniq`; do
    echo "${fn},index,setme" >>$SC4S_ETC/conf.d/local/context/splunk_metadata.csv.example
done

echo syslog-ng checking config
export SC4S_VERSION=$(cat $SC4S_ETC/VERSION)
echo sc4s version=$(cat $SC4S_ETC/VERSION)
echo sc4s version=$(cat $SC4S_ETC/VERSION) >>$SC4S_VAR/log/syslog-ng.out
$SC4S_SBIN/syslog-ng --no-caps $SC4S_CONTAINER_OPTS -s >>$SC4S_VAR/log/syslog-ng.out 2>$SC4S_VAR/log/syslog-ng.err

# Use goss to pick up default listening ports for health check
if command -v goss &> /dev/null
then
  echo starting goss
  goss -g $SC4S_ETC/goss.yaml serve -l 0.0.0.0:$SC4S_LISTEN_STATUS_PORT --format json >/dev/null 2>/dev/null &
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
