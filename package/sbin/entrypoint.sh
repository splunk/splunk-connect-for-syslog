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

/opt/net-snmp/sbin/snmptrapd -Lf /opt/syslog-ng/var/log/snmptrapd.log

echo syslog-ng checking config
echo sc4s version=$(cat /VERSION)
echo sc4s version=$(cat /VERSION) >/opt/syslog-ng/var/log/syslog-ng.out
/opt/syslog-ng/sbin/syslog-ng -s >>/opt/syslog-ng/var/log/syslog-ng.out 2>/opt/syslog-ng/var/log/syslog-ng.err

echo syslog-ng starting
/opt/syslog-ng/bin/persist-tool add /opt/syslog-ng/etc/reset_persist -o /opt/syslog-ng/var

/opt/syslog-ng/sbin/syslog-ng $@ &
pid="$!"
# wait forever
if [[ $@ != *"-s"* ]]; then
  while true
  do
    tail -f /dev/null & wait ${!}
  done
fi
