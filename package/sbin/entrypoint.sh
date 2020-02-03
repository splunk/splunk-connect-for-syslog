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

gomplate $(find . -name *.tmpl | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=etc/go_templates/

mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context/
for file in /opt/syslog-ng/etc/conf.d/local/context/*.example ; do cp --verbose -n $file ${file%.example}; done
cp --verbose -R /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/

echo syslog-ng checking config
echo sc4s version=$(cat /VERSION)
echo sc4s version=$(cat /VERSION) >/var/log/syslog-ng.out
/opt/syslog-ng/sbin/syslog-ng -s >>/var/log/syslog-ng.out 2>/var/log/syslog-ng.err

echo syslog-ng starting
exec /opt/syslog-ng/sbin/syslog-ng $@
