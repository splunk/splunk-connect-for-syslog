## Meraki (MR, MS, MX)

## Key facts
* In most cases, Cisco Meraki logs are general and require vendor product by source configuration.
* For distinctive log messages, filters are based on the appliance name and program value.

## Distinctive log messages
See samples in the [vendor documentation](https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Syslog_Event_Types_and_Log_Samples).

The two conjuncted conditions are required:

1. Program: `(events|urls|firewall|cellular_firewall|vpn_firewall|ids-alerts|flows)`

2. Appliance name:

| Sourcetype | Distinct element |
| ---------  | --------------   |
| meraki:accesspoints | `host('MR' type(string) flags(ignore-case,prefix))` |
| meraki:securityappliances | `host('MX' type(string) flags(ignore-case,prefix))` |
| meraki:switches | `host('MS' type(string) flags(ignore-case,prefix))` |
 

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/5580>                                                                 |
| Product Manual | <https://documentation.meraki.com/zGeneral_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration> <https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Syslog_Event_Types_and_Log_Samples> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| meraki:accesspoints    | MR                                                                                                |
| meraki:securityappliances    | MX                                                                                              |
| meraki:switches    | MS                                                                                             |
| meraki | vendor product by source configuration |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_meraki_accesspoints     | meraki:accesspoints    | netfw          | Filtered on the message format |
| cisco_meraki_securityappliances     | meraki:securityappliances    | netfw          | Filtered on the message format |
| cisco_meraki_switches     | meraki:switches    | netfw          | Filtered on the message format |
| cisco_meraki | meraki | netfw | Filtered on vendor product by source configuration |

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
