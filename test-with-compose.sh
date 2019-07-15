#!/usr/bin/env bash
#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause

mkdir test-results
docker volume create sc4s-tests
docker volume create sc4s-results

docker container create --name dummy \
        -v sc4s-tests:/work/tests \
        -v sc4s-results:/work/test-results \
        registry.access.redhat.com/ubi7/ubi
docker cp tests/ dummy:/work/tests/
docker rm dummy

docker-compose build --build-arg  RH_ACTIVATION=$RH_ACTIVATION --build-arg  RH_ORG=$RH_ORG
docker-compose up  --abort-on-container-exit --exit-code-from test

docker container create --name dummy \
        -v sc4s-tests:/work/tests \
        -v sc4s-results:/work/test-results \
        registry.access.redhat.com/ubi7/ubi

docker cp dummy:/work/test-results/functional test-results
docker rm dummy
EXIT=$0
