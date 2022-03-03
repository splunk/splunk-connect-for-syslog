# Meeting Management

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                               |
| Product Manual | multiple |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:mm:system:*     |  final component take from the program field of the message header                                                                                             |
| cisco:mm:audit     |  Requires setup of vendor product by source see below                                                                                            |


## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_mm_system    | cisco:mm:system:*    | netops          | None     |
| cisco_mm_audit    | cisco:mm:audit    | netops          | None     |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-cisco_mm.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-cisco_mm[sc4s-vps] {
 filter { 
        host('^test-cmm-')
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('cisco')
            product('mm')
        ); 
    };   
};


```
