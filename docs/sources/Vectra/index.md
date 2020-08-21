# Vendor - Vectra

## Product - Cognito

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Technology Add-On for Vectra Cognito | https://splunkbase.splunk.com/app/4408/                                                           |


### Sourcetypes

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


### Filter type

MSG Parse: This filter parses message content

### Options

Note: listed for reference; processing utilizes the Microsoft ArcSight log path as this format is a subtype of CEF

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_CEF | no | Enable archive to disk for this specific source |
| SC4S_DEST_CEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

* NOTE:  Set only _one_ set of CEF variables for the entire SC4S deployment, regardless of how
many ports are in use by this CEF source (or any others).  See the "Common Event Format" source
documentation for more information.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected

```
index=<asconfigured> (sourcetype="deepsecurity*")
```
