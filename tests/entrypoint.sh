#!/bin/sh
echo Check for sc4s
wait-for sc4s:514
echo check for splunk web
wait-for splunk:8000
echo check for splunk web
wait-for splunk:8000
echo check for splunk web
wait-for splunk:8000
echo check for splunk web
wait-for splunk:8000

echo check for splunk mgmt
wait-for splunk:8089
echo check for splunk mgmt
wait-for splunk:8089
echo check for splunk mgmt
wait-for splunk:8089
echo check for splunk mgmt
wait-for splunk:8089

echo check for splunk hec
wait-for splunk:8088
echo check for splunk hec
wait-for splunk:8088
echo check for splunk hec
wait-for splunk:8088
echo check for splunk hec
wait-for splunk:8088

cd /work;python -m pytest --junitxml=/work/test-results/functional/functional.xml
