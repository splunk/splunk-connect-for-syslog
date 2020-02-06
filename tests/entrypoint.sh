#!/bin/sh

cd /work
pytest -v \
       --splunk_type=external \
       --splunk_password=${SPLUNK_PASSWORD} \
       --sc4s_host=sc4s \
       --splunk_host=splunk \
       --junitxml=/work/test-results/functional/functional.xml $@
