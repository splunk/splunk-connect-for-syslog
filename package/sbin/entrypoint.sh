#!/usr/bin/env bash
source scl_source enable rh-python36

export SC4S_LISTEN_DEFAULT_TCP_PORT=514
export SC4S_LISTEN_DEFAULT_UDP_PORT=514

cd /opt/syslog-ng

gomplate $(find . -name *.tmpl | sed -E 's/^(\/.*\/)*(.*)\..*$/--file=\2.tmpl --out=\2/') --template t=etc/go_templates/


mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp --verbose -n /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context/
cp --verbose -R /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/

echo syslog-ng checking config
/opt/syslog-ng/sbin/syslog-ng -s >/var/log/syslog-ng.out 2>/var/log/syslog-ng.err

echo syslog-ng starting
exec /opt/syslog-ng/sbin/syslog-ng $@