#!/usr/bin/env bash
#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause
WAITON=${1:-test}
compose=${2:-docker-compose.yml}
echo $WAITON $compose
mkdir test-results
docker-compose down
docker volume rm sc4s-results
docker volume rm splunk-etc

docker volume create sc4s-results
docker volume create splunk-etc

docker container create --name dummy \
        -v sc4s-results:/work/test-results \
        -v splunk-etc:/work/splunk-etc \
        registry.access.redhat.com/ubi7/ubi
docker cp ./splunk/etc/* dummy:/work/splunk-etc/
docker rm dummy

docker-compose -f $compose pull splunk
docker-compose -f $compose build
docker-compose -f $compose up -d splunk
docker-compose -f $compose up -d sc4s
sleep 60

docker-compose -f $compose up --abort-on-container-exit --exit-code-from $WAITON

docker container create --name dummy \
        -v sc4s-results:/work/test-results \
        registry.access.redhat.com/ubi7/ubi

docker cp dummy:/work/test-results/functional test-results
docker rm dummy
EXIT=$0
