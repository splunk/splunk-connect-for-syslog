# Cognito

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Technology Add-On for Vectra Cognito | <https://splunkbase.splunk.com/app/4408/>                                                           |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
|vectra:cognito:detect       ||
|vectra:cognito:accountdetect       ||
|vectra:cognito:accountscoring       ||
|vectra:cognito:audit       ||
|vectra:cognito:campaigns       ||
|vectra:cognito:health       ||
|vectra:cognito:hostscoring       ||
|vectra:cognito:accountlockdown       ||

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
|Vectra Networks_X Series|vectra:cognito:detect       |main|
|Vectra Networks_X Series_accountdetect|vectra:cognito:accountdetect       |main|
|Vectra Networks_X Series_asc|vectra:cognito:accountscoring       |main|
|Vectra Networks_X Series_audit|vectra:cognito:audit       |main|
|Vectra Networks_X Series_campaigns|vectra:cognito:campaigns       |main|
|Vectra Networks_X Series_health|vectra:cognito:health       |main|
|Vectra Networks_X Series_hsc|vectra:cognito:hostscoring       |main|
|Vectra Networks_X Series_lockdown|vectra:cognito:accountlockdown       |main|
