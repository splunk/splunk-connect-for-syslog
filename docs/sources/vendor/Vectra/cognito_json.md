# Cognito JSON

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Technology Add-On for Vectra Detect (JSON) | <https://splunkbase.splunk.com/app/5271>                                                           |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
|vectra:cognito:detect:json||
|vectra:cognito:hostscoring:json||
|vectra:cognito:hostdetect:json||
|vectra:cognito:hostlockdown:json||
|vectra:cognito:accountscoring:json||
|vectra:cognito:accountdetect:json||
|vectra:cognito:accountlockdown:json||
|vectra:cognito:campaigns:json||
|vectra:cognito:audit:json||
|vectra:cognito:health:json||

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
|vectra_cognito detect_detect |vectra:cognito:detect:json |main|
|vectra_cognito detect_hostscoring |vectra:cognito:hostscoring:json |main|
|vectra_cognito detect_hostdetect |vectra:cognito:hostdetect:json |main|
|vectra_cognito detect_hostlockdown |vectra:cognito:hostlockdown:json |main|
|vectra_cognito detect_accountscoring |vectra:cognito:accountscoring:json |main|
|vectra_cognito detect_accountdetect |vectra:cognito:accountdetect:json |main|
|vectra_cognito detect_accountlockdown |vectra:cognito:accountlockdown:json |main|
|vectra_cognito detect_campaigns |vectra:cognito:campaigns:json |main|
|vectra_cognito detect_audit |vectra:cognito:audit:json |main|
|vectra_cognito detect_health |vectra:cognito:health:json |main|
