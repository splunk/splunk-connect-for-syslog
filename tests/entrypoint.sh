#!/bin/sh
wait-for sc4s:514
wait-for splunk:9997
wait-for splunk:8000
wait-for splunk:8089
wait-for splunk:8088

cd /work;python -m pytest --junitxml=/work/test-results/functional/functional.xml
