#!/usr/bin/env bash
#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause

mkdir test-results
docker volume create sc4s-tests

docker container create --name dummy \
        -v sc4s-tests:/work/tests \
        registry.access.redhat.com/ubi7/ubi
docker cp tests/ dummy:/work/tests/
docker rm dummy

docker-compose pull
docker-compose up

EXIT=$0


