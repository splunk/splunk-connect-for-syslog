#!/usr/bin/env bash
source scl_source enable rh-python36
gomplate -V \
    --input-dir=/opt/syslog-ng/etc/conf.d/log_paths/ \
    --output-map='/opt/syslog-ng/etc/conf.d/log_paths/{{ .in | strings.ReplaceAll ".conf.tmpl" ".conf" }}'

exec /opt/syslog-ng/sbin/syslog-ng $@