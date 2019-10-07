#!/usr/bin/env bash
source scl_source enable rh-python36

cd /opt/syslog-ng
for d in $(find /opt/syslog-ng/etc -type d)
do
  echo Templating conf for $d
  gomplate \
    --input-dir=$d \
    --template t=etc/go_templates/  \
    --exclude=*.conf --exclude=*.csv --exclude=*.t --exclude=.*\
    --output-map="$d/{{ .in | strings.ReplaceAll \".conf.tmpl\" \".conf\" }}"
done

mkdir -p /opt/syslog-ng/etc/conf.d/local/context/
mkdir -p /opt/syslog-ng/etc/conf.d/local/config/
cp --verbose -n /opt/syslog-ng/etc/context_templates/* /opt/syslog-ng/etc/conf.d/local/context/
cp --verbose -R -n /opt/syslog-ng/etc/local_config/* /opt/syslog-ng/etc/conf.d/local/config/

echo syslog-ng starting
exec /opt/syslog-ng/sbin/syslog-ng $@