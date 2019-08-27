#!/bin/sh
echo Check for sc4s
wait-for sc4s:514 -t 0 -- echo scs is up
echo check for splunk web
wait-for splunk:8000 -t 0 -- echo splunkweb is up
echo check for splunk mgmt
wait-for splunk:8089 -t 0 -- echo splunkmgmt is up
echo check for splunk hec
wait-for splunk:8088 -t 0 -- echo splunkhec is up

sleep 30

echo Check for sc4s
wait-for sc4s:514 -t 0 -- echo scs is up
echo check for splunk web
wait-for splunk:8000 -t 0 -- echo splunkweb is up
echo check for splunk mgmt
wait-for splunk:8089 -t 0 -- echo splunkmgmt is up
echo check for splunk hec
wait-for splunk:8088 -t 0 -- echo splunkhec is up


cd /work;python -m pytest --junitxml=/work/test-results/functional/functional.xml
