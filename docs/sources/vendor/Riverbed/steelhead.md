# SteelHead

## Key facts

* Partial MSG Format based filter
* RFC5424 or Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| riverbed:steelhead        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| riverbed_syslog_steelhead      | riverbed:steelhead        | netops          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-riverbed_syslog.conf
#File name provided is a suggestion it must be globally unique

application app-vps-riverbed_syslog[sc4s-vps] {
 filter {      
        host(....)
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('riverbed')
            product('syslog')
        ); 
    };   
};

```
