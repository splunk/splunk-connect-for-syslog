#1. Initialization & Helper Functions
#!/usr/bin/env bash
set -euo pipefail

join_by() {
  local d="$1"; shift
  printf "%s" "$1" "${@/#/$d}"
}


#2. Python Env & Parser Cache

source /var/lib/python-venv/bin/activate
export PYTHONPATH=/etc/syslog-ng/pylib
python3 /etc/syslog-ng/pylib/parser_source_cache.py



#Default Ports & Config Variables

export SC4S_LISTEN_STATUS_PORT=${SC4S_LISTEN_STATUS_PORT:-8080}
export SC4S_LISTEN_DEFAULT_TCP_PORT=${SC4S_LISTEN_DEFAULT_TCP_PORT:-514}
export SC4S_LISTEN_DEFAULT_UDP_PORT=${SC4S_LISTEN_DEFAULT_UDP_PORT:-514}
export SC4S_LISTEN_DEFAULT_TLS_PORT=${SC4S_LISTEN_DEFAULT_TLS_PORT:-6514}
export SC4S_LISTEN_DEFAULT_RFC5426_PORT=${SC4S_LISTEN_DEFAULT_RFC5426_PORT:-601}
export SC4S_LISTEN_DEFAULT_RFC6587_PORT=${SC4S_LISTEN_DEFAULT_RFC6587_PORT:-601}
export SC4S_LISTEN_DEFAULT_RFC5425_PORT=${SC4S_LISTEN_DEFAULT_RFC5425_PORT:-5425}
export SC4S_CLEAR_NAME_CACHE=${SC4S_CLEAR_NAME_CACHE:-no}
export SC4S_DEFAULT_TIMEZONE=${SC4S_DEFAULT_TIMEZONE:-GMT}
export SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL_SECONDS=${SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL_SECONDS:-2}
export SC4S_DEST_SPLUNK_INDEXED_FIELDS=${SC4S_DEST_SPLUNK_INDEXED_FIELDS:-r_unixtime,facility,container,loghost,destport,fromhostip,proto,severity}
export SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX=${SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX:-fgt}





#Backward Compatibility

if [ ! -z "${SPLUNK_HEC_URL:-}" ]; then
  export SC4S_DEST_SPLUNK_HEC_DEFAULT_URL=$SPLUNK_HEC_URL
fi

if [ ! -z "${SPLUNK_HEC_TOKEN:-}" ]; then
  export SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN=$SPLUNK_HEC_TOKEN
fi

if [ ! -z "${SC4S_DEST_SPLUNK_HEC_TLS_VERIFY:-}" ]; then
  export SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_VERIFY=$SC4S_DEST_SPLUNK_HEC_TLS_VERIFY
fi



#Paths

export SC4S_ETC=${SC4S_ETC:-/etc/syslog-ng}
export SC4S_TLS=${SC4S_TLS:-/etc/syslog-ng/tls}
export SC4S_VAR=${SC4S_VAR:-/var/lib/syslog-ng}
export SC4S_BIN=${SC4S_BIN:-/usr/bin}
export SC4S_SBIN=${SC4S_SBIN:-/usr/sbin}



#Alternate Destinations

SC4S_DESTS_FILTERED_ALTERNATES=$(env | grep _FILTERED_ALTERNATES= | grep -v SC4S_DEST_GLOBAL_FILTERED_ALTERNATES | cut -d= -f2 | sort -u | paste -s -d, -)
if [ "$SC4S_DESTS_FILTERED_ALTERNATES" == "" ]; then
  unset SC4S_DESTS_FILTERED_ALTERNATES
else
  export SC4S_DESTS_FILTERED_ALTERNATES
fi


#Signal Handlers
term_handler() {
  if [ ${pid:-0} -ne 0 ]; then
    echo "Terminating syslog-ng..."
    kill -SIGTERM "$pid"
    wait "$pid"
    exit $?
  fi
  exit 143
}

hup_handler() {
  if [ ${pid:-0} -ne 0 ]; then
    echo "Reloading syslog-ng..."
    kill -SIGHUP "$pid"
  fi
}

quit_handler() {
  if [ ${pid:-0} -ne 0 ]; then
    echo "Quitting syslog-ng..."
    kill -SIGQUIT "$pid"
    wait "$pid"
  fi
}

trap 'kill ${!}; hup_handler' SIGHUP
trap 'kill ${!}; term_handler' SIGTERM
trap 'kill ${!}; quit_handler' SIGQUIT


#Directory Setup

mkdir -p \
  $SC4S_VAR/log/ \
  $SC4S_ETC/conf.d/local/context/ \
  $SC4S_ETC/conf.d/merged/context/ \
  $SC4S_ETC/conf.d/local/config/app_parsers/ \
  $SC4S_ETC/local_config/ \
  $SC4S_ETC/addons/

cp -f $SC4S_ETC/context_templates/* $SC4S_ETC/conf.d/local/context/



#Config Generation

echo "Generating configuration from templates..."
python3 /etc/syslog-ng/pylib/load_env.py



#Optional Name Cache Cleanup

if [ "${SC4S_CLEAR_NAME_CACHE}" = "yes" ]; then
  echo "Clearing name cache..."
  rm -f $SC4S_VAR/db/*
fi


#HEC Endpoint Healthcheck

if [ ! -z "${SC4S_DEST_SPLUNK_HEC_DEFAULT_URL:-}" ]; then
  echo "Checking HEC endpoint readiness..."
  curl -k -s -S --max-time 3 \
    -H "Authorization: Splunk $SC4S_DEST_SPLUNK_HEC_DEFAULT_TOKEN" \
    "$SC4S_DEST_SPLUNK_HEC_DEFAULT_URL/services/collector/health" || echo "HEC endpoint not available"
fi



#TLS Cert/Key Verification

if [ -f "${SC4S_TLS}/tls.key" ]; then
  echo "Verifying TLS private key matches public certificate..."
  diff <(openssl x509 -noout -modulus -in ${SC4S_TLS}/tls.crt | openssl md5) \
       <(openssl rsa -noout -modulus -in ${SC4S_TLS}/tls.key | openssl md5) || {
         echo "TLS private key does not match public certificate."
         exit 1
       }
fi



#Optional setup.sh
if [ -f /etc/syslog-ng/setup.sh ]; then
  echo "Running setup.sh..."
  chmod +x /etc/syslog-ng/setup.sh
  /etc/syslog-ng/setup.sh
fi


#Run syslog-ng
echo "Starting syslog-ng..."
/usr/sbin/syslog-ng -F -R /dev/stdout -R /dev/stderr &
pid=$!

wait $pid
