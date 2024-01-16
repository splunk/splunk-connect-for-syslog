# Cisco Networking (IOS and Compatible)

Cisco Network Products of multiple types share common logging characteristics the following types are known to be compatible:

* Cisco AireOS (AP & WLC)
* Cisco APIC/ACI
* Cisco IOS
* Cisco IOS-XR
* Cisco IOS-XE
* Cisco NX-OS
* Cisco FX-OS

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/1467/>                                                                 |
| IOS Manual     | <https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst2960/software/release/12-2_55_se/configuration/guide/scg_2960/swlog.html> |
| NX-OS Manual   | <https://www.cisco.com/c/en/us/td/docs/switches/datacenter/nexus9000/sw/6-x/system_management/configuration/guide/b_Cisco_Nexus_9000_Series_NX-OS_System_Management_Configuration_Guide/sm_5syslog.html>|
| Cisco ACI      | <https://community.cisco.com/legacyfs/online/attachments/document/technote-aci-syslog_external-v1.pdf> |
| Cisco WLC & AP | <https://www.cisco.com/c/en/us/support/docs/wireless/4100-series-wireless-lan-controllers/107252-WLC-Syslog-Server.html#anc8> |
| Cisco IOS-XR | <https://www.cisco.com/c/en/us/td/docs/iosxr/cisco8000/system-monitoring/73x/b-system-monitoring-cg-cisco8k-73x/implementing_system_logging.html> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:ios      | This source type is also used for NX-OS, ACI and WLC product lines                                      |
| cisco:xr       | This source type is used for Cisco IOS XR                                     |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_ios      | cisco:ios      | netops          | none          |
| cisco_xr      | cisco:xr      | netops          | none          |

### Filter type

* Cisco IOS products can be identified by message parsing alone
* Cisco WLC, and ACI products must be identified by host or ip assignment update the filter `f_cisco_ios` as required

## Setup and Configuration

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
  * timestamp is included and millisecond accuracy selected
* ACI Logging configuration of the ACI product often varies by use case.
  * Ensure NTP sync is configured and active
  * Ensure proper host names are configured
* WLC
  * Ensure NTP sync is configured and active
  * Ensure proper host names are configured
  * For security use cases per AP logging is required


If you want to send raw logs to splunk (without any drop) then only use this feature
Please set following property in env_file:
```
SC4S_ENABLE_CISCO_IOS_RAW_MSG=yes
```
Restart SC4S and it will send entire message without any drop.

* NOTE: Please use this feature only when there is a special need to get entire raw message. This is not supported by splunk.
