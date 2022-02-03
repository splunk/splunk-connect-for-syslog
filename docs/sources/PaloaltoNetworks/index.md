# Vendor - PaloAlto

## Product - NGFW

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2757/                                                                 |
| Product Manual | https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-admin/monitoring/use-syslog-for-monitoring/configure-syslog-monitoring.html                                                         |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| pan:log        | None                                                                                                    |
| pan:pan_globalprotect | none |
| pan:traffic    | None                                                                                         |
| pan:threat     | None                                                                                          |
| pan:system     | None                                                                                          |
| pan:config     | None                                                                                          |
| pan:hipmatch   | None                                                                                          |
| pan:correlation | None                                                                                          |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| pan_panos_log      | pan:log       | netops          | none          |
| pan_panos_globalprotect | pan:pan_globalprotect | netfw | none |
| pan_tpanos_raffic    | pan:traffic      | netfw          | none          |
| pan_panos_threat    | pan:threat      | netproxy          | none          |
| pan_panos_system    | pan:system      | netops          | none          |
| pan_panos_config    | pan:config      | netops          | none          |
| pan_panos_hipmatch    | pan:hipmatch      | netops          | none          |
| pan_panos_correlation    | pan:correlation      | netops          | none          |

### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the admin manual for specific details of configuration
    * Select TCP or SSL transport option
    * Select IETF Format
    * Ensure the format of the event is not customized

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_PULSE_PAN_PANOS_RFC6587_PORT      | empty string      | Enable a TCP using IETF Framing (RFC6587) port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_PAN_PANOS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_PAN_PANOS | no | Enable archive to disk for this specific source |
| SC4S_DEST_PAN_PANOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active firewall will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=pan:*| stats count by host
```
## Product - Cortext

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2757/                                                                 |

### Sourcetypes

| sourcetype               | notes |
|--------------------------|-------|
| pan:*| | Sourcetypes and keys compatible with NGFW are supported |
| pan:xsoar              | none  |

### Index Configuration

| key                        | index    | notes          |
|----------------------------|----------|----------------|
| Palo Alto Networks_Palo Alto Networks Cortex XSOAR  | epintel   | none           |

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
index=<asconfigured> (sourcetype=pan:xsoar)
```


## Product - TRAPS

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2757/                                                                 |

### Sourcetypes

| sourcetype               | notes |
|--------------------------|-------|
| pan:traps4              | none  |

### Index Configuration

| key                        | index    | notes          |
|----------------------------|----------|----------------|
| Palo Alto Networks_Traps Agent  | epintel   | none           |

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
index=<asconfigured> (sourcetype=pan:traps4)
```
