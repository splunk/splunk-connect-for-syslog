#!/bin/sh

cd /work
pytest -v \
       --splunk_test=external \
       --splunk_password=${SPLUNK_PASSWORD} \
       --junitxml=/work/test-results/functional/functional.xml $@
