# Vendor - FireEye

## Product - CMS,eMPS

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Technology Add-On for FireEye | https://splunkbase.splunk.com/app/1904/                                                          |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| fe_cef_syslog       ||


### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| FireEye_CMS |fe_cef_syslog       |netids|
| FireEye_eMPS |fe_cef_syslog       |netids|

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
index=<asconfigured> (sourcetype="fe_cef_syslog")
```
