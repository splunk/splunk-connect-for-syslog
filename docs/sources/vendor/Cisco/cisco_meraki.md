## Meraki (MR, MS, MX, MV)

## Key facts

* MSG Format based filter (Partial)
* Requires vendor product by source configuration
* None conformant legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3018/>                                                                 |
| Product Manual | <https://documentation.meraki.com/zGeneral_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| meraki     | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_meraki     | meraki    | netfw          | The current TA does not sub sourcetype or utilize source preventing segmentation into more appropriate indexes |

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
