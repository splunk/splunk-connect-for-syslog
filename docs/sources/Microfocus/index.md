# Vendor - MicroFocus Arcsight

## Product - Arcsight Internal Agent

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | https://github.com/splunk/splunk-add-on-for-cefdownloads/                                                              |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

### Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ArcSight:ArcSight        | Internal logs                                                                                               |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ArcSight_ArcSight      | ArcSight:ArcSight      | main          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |

* NOTE:  Set only _one_ set of CEF variables for the entire SC4S deployment, regardless of how
many ports are in use by this CEF source (or any others).  See the "Common Event Format" source
documentation for more information.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=cef source="ArcSight:ArcSight")
```

## Product - Arcsight Microsoft Windows (CEF)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | https://bitbucket.org/SPLServices/ta-cef-for-splunk/downloads/                                                              |
| Splunk Add-on CEF | https://bitbucket.org/SPLServices/ta-cef-microsoft-windows-for-splunk/downloads/                                                             |
| Product Manual | https://docs.imperva.com/bundle/cloud-application-security/page/more/log-configuration.htm                                                        |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

### Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| CEFEventLog:System or Application Event     | Windows Application and System Event Logs                                                                                  |
| CEFEventLog:Microsoft Windows     | Windows Security Event Logs                                                                                 |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Microsoft_System or Application Event      | CEFEventLog:System or Application Event      | oswin          | none          |
| Microsoft_Microsoft Windows      | CEFEventLog:Microsoft Windows      | oswinsec         | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

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
index=<asconfigured> (sourcetype=cef (source="CEFEventLog:Microsoft Windows" OR source="CEFEventLog:System or Application Event"))
```
