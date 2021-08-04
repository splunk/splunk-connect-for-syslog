#!/usr/bin/env bash

echo publish $1 $2

docker pull ghcr.io/splunk-connect-for-syslog:splunk-connect-for-syslog:$1
docker save ghcr.io/splunk-connect-for-syslog:splunk-connect-for-syslog:$1 | gzip -c > /tmp/workspace/oci_container.tar.gz