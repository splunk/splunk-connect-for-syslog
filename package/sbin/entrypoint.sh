#!/usr/bin/env bash
source scl_source enable rh-python36
gomplate -V \
    --input-dir=/opt/syslog-ng/etc/conf.d/log_paths \
    --include=*.tmpl \
    --output-map='{{ .in | strings.ReplaceAll ".conf.tmpl" ".conf" }}'
    --output-dir=/opt/syslog-ng/etc/conf.d/log_paths
exec /opt/syslog-ng/sbin/syslog-ng $@