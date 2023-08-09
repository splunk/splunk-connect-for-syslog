## Meraki (MR, MS, MX)

## Key facts
* For distinctive log messages filters are based on MSG Formats. 
* Indistinctive log messages require vendor product by source configuration.

## Distinctive log messages
See samples in the [vendor documentation](https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Syslog_Event_Types_and_Log_Samples).

| Sourcetype | Distinct element |
| ---------  | --------------   |
| cisco:meraki:accesspoints | `program("MR" type(string) flags(prefix)) or message("airmarshal_events")` |
| cisco:meraki:securityappliances | `program("MX" type(string) flags(prefix)) or message("Site-to-site VPN"))` |
| cisco:meraki:switches | `program("MS" type(string) flags(prefix)` |
 


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/5580>                                                                 |
| Product Manual | <https://documentation.meraki.com/zGeneral_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration> <https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Syslog_Event_Types_and_Log_Samples> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:meraki:accesspoints    | MR (messages/roles: Event Log, URLs, and Flows)                                                                                                   |
| cisco:meraki:securityappliances    | MX (messages/roles: Event Log, IDS Alerts, URLs, and Flows)                                                                                                   |
| cisco:meraki:switches    | MS (messages/roles: Event Log)                                                                                                   |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_meraki_accesspoints     | cisco:meraki:accesspoints    | netfw          | Filtered on the message format |
| cisco_meraki_securityappliances     | cisco:meraki:securityappliances    | netfw          | Filtered on the message format |
| cisco_meraki_switches     | cisco:meraki:switches    | netfw          | Filtered on the message format |
| cisco_meraki | cisco:meraki | netfw | Filtered on vendor product by source configuration |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-cisco_meraki.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-cisco_meraki[sc4s-vps] {
 filter { 
        host("^testcm-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('cisco')
            product('meraki')
        ); 
    };   
};
```
