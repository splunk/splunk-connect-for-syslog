#!/usr/bin/env bash
set -e

echo publish $1 $2
tags=$(echo $CONTAINER_SOURCE_IMAGE |sed 's|ghcr.io/splunk/splunk-connect-for-syslog/container|docker.io/splunk/scs|g')
/tmp/regctl image copy $CONTAINER_SOURCE_IMAGE docker.io/splunk/scs:$1
for line in $tags; do echo working on "$line"; /tmp/regctl image copy docker.io/splunk/scs:$1 $line; done
