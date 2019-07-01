#!/usr/bin/env bash

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


