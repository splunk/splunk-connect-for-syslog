# Vendor - Cisco

## Product - ACS

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/1811/                                                                 |
| Product Manual | https://community.cisco.com/t5/security-documents/acs-5-x-configuring-the-external-syslog-server/ta-p/3143143 |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:acs     | Aggregation used                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_acs    | cisco:acs    | netauth          | None     |


### Filter type

PATTERN MATCH

### Setup and Configuration

* No special steps required

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_ACS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CISCO_ACS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CISCO_ACS | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_ACS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cisco:acs
```

Verify timestamp, and host values match as expected    

## Product - APIC (ACI)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | No current add-on for syslog events                                                                 |
| Product Manual | https://community.cisco.com/t5/security-documents/acs-5-x-configuring-the-external-syslog-server/ta-p/3143143 |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:apic:acl: | APIC events from leaf switches |
| cisco:apic:events     | APIC events from any component used                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_apic_acl    | cisco:apic:acl    | netfw          | None     |
| cisco_apic_events    | cisco:apic:events    | netops          | None     |

### Filter type

PATTERN MATCH

### Setup and Configuration

* No special steps required

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_APIC_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CISCO_APIC_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CISCO_APIC | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_APIC_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cisco:apic:*
```

Verify timestamp, and host values match as expected    

## Product - ASA AND FTD (Firepower)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/1620/                                                                 |
| Product Manual | https://www.cisco.com/c/en/us/td/docs/security/asa/asa82/configuration/guide/config/monitor_syslog.html |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:asa      | cisco FTD Firepower will also use this source type                                                      |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_asa      | cisco:asa      | netfw          | none           |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Follow vendor configuration steps per Product Manual above ensure:
    * Log Level is 6 "Informational"
    * Protocol is TCP/IP
    * permit-hostdown is on
    * device-id is hostname and included
    * timestamp is included

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_ASA_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CISCO_ASA_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CISCO_ASA | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_ASA_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_LISTEN_CISCO_ASA_LEGACY_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined expecting RFC3164 format |
| SC4S_LISTEN_CISCO_ASA_LEGACY_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined expecting RFC3164 format |
| SC4S_ARCHIVE_CISCO_ASA_LEGACY | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_ASA_LEGACY_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cisco:asa
```

Verify timestamp, and host values match as expected    

## Product - IOS and NX-OS based equipment

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/1467/                                                                 |
| IOS Manual     | https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst2960/software/release/12-2_55_se/configuration/guide/scg_2960/swlog.html |
| NX-OS Manual   | https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/6-x/system_management/configuration/guide/b_Cisco_Nexus_9000_Series_NX-OS_System_Management_Configuration_Guide/sm_5syslog.html|
| Cisco ACI      | https://community.cisco.com/legacyfs/online/attachments/document/technote-aci-syslog_external-v1.pdf |
| Cisco WLC & AP | https://www.cisco.com/c/en/us/support/docs/wireless/4100-series-wireless-lan-controllers/107252-WLC-Syslog-Server.html#anc8 |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:ios      | This source type is also used for NX-OS, ACI and WLC product lines                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_ios      | cisco:ios      | netops          | none          |
| cisco_nx_os    | cisco:ios      | netops          | none          |

### Filter type

* Cisco IOS products can be identified by message parsing alone
* Cisco NX OS, WLC, and ACI products must be identified by host or ip assignment update the filter `f_cisco_nx_os` as required


### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* IOS Follow vendor configuration steps per Product Manual above ensure:
    * Ensure a reliable NTP server is set and synced
    * Log Level is 6 "Informational"
    * Protocol is TCP/IP
    * permit-hostdown is on
    * device-id is hostname and included
    * timestamp is included
* NX-OS Follow vendor configuration steps per Product Manual above ensure:
    * Ensure a reliable NTP server is set and synced
    * Log Level is 6 "Informational" user may select alternate levels by module based on use cases
    * Protocol is TCP/IP
    * device-id is hostname and included
    * timestamp is included and milisecond accuracy selected
* ACI Logging configuration of the ACI product often varies by use case.
    * Ensure NTP sync is configured and active
    * Ensure proper host names are configured
* WLC
    * Ensure NTP sync is configured and active
    * Ensure proper host names are configured
    * For security use cases per AP logging is required

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_IOS_UDP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CISCO_IOS_TCP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CISCO_IOS | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_IOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_LISTEN_CISCO_NX_OS_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CISCO_NX_OS_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CISCO_NXOS | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_NXOS_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present, for NX-OS, WLC and ACI products ensure each host filter condition is verified

```
index=<asconfigured> sourcetype=cisco:ios | stats count by host
```

## Product - ISE

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/1915/                                                                 |
| Product Manual | https://www.cisco.com/c/en/us/td/docs/security/ise/2-6/Cisco_ISE_Syslogs/Cisco_ISE_Syslogs/Cisco_ISE_Syslogs_chapter_00.html |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:ise:syslog     | Aggregation used                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_ise     | cisco:ise:syslog    | netauth          | None     |


### Filter type

PATTERN MATCH

### Setup and Configuration

* No special steps required

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_ISE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined expecting RFC5424 format |
| SC4S_LISTEN_CISCO_ISE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined expecting RFC5424 format |
| SC4S_ARCHIVE_CISCO_ISE | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_ISE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cisco:ise:syslog
```

Verify timestamp, and host values match as expected    

## Product - Meraki Product Line MR, MS, MX, MV

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3018/                                                                 |
| Product Manual | https://documentation.meraki.com/zGeneral_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| merkai     | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_meraki     | meraki    | netfw          | The current TA does not sub sourcetype or utilize source preventing segmenation into more appropriate indexes           |


### Filter type

IP, Netmask, Host or Port

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Follow vendor configuration steps per Product Manual above

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_MERAKI_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined expecting RFC5424 format |
| SC4S_LISTEN_CISCO_MERAKI_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined expecting RFC5424 format |
| SC4S_ARCHIVE_CISCO_MERAKI | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_MERAKI_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=merkai
```

Verify timestamp, and host values match as expected    

## Product - UCM

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                               |
| Product Manual | multiple |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:ucm     |  None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_ucm    | cisco:ucm    | ucm          | None     |


### Filter type

PATTERN MATCH

### Setup and Configuration

* Refer to Cisco support web site

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CISCO_UCM_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_CISCO_UCM_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_CISCO_UCM | no | Enable archive to disk for this specific source |
| SC4S_DEST_CISCO_UCM_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cisco:ucm
```

Verify timestamp, and host values match as expected    