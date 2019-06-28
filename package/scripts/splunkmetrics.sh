#!/bin/bash
sleep 30
while sleep 10
do
  TS=$(date +"%s")
  tmpfilecsv=$(mktemp /tmp/syslog-ng-stats-XXXXXXX-csv)
  tmpfilejson=$(mktemp /tmp/syslog-ng-stats-XXXXXXX-json)
  /opt/syslog-ng/sbin/syslog-ng-ctl query get "*" --reset | tail -n +2 | grep \^. | grep -v "^The selected counters" >$tmpfilecsv
  IFS=';'
  while read -r SourceName SourceId SourceInstance State Type Number
  do
     echo	"{
     \"time\":\"$TS.000\",
     \"event\":\"metric\",
     \"source\":\"syslog-ng\",
     \"host\":\"$HOSTNAME\",
     \"index\":\"$SPLUNK_METRICS_INDEX\",
     \"fields\":{
        \"SourceId\":\"$SourceId\",
        \"SourceInstance\":\"$SourceInstance\",
        \"State\":\"$State\",
        \"Type\":\"$Type\",
        \"_value\":$Number,
        \"metric_name\":\"$SourceName\"
     }
  } ">>$tmpfilejson
  done < $tmpfilecsv

  curl -s -S -k $SPLUNK_HEC_STATSURL -H "Authorization: Splunk $SPLUNK_HEC_TOKEN" -d "@$tmpfilejson"
done
