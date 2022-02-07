# CMC (VRTX)

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                            |
| Add-on Manual | <https://www.dell.com/support/manuals/en-us/dell-chassis-management-controller-v3.10-dell-poweredge-vrtx/cmcvrtx31ug/overview?guid=guid-84595265-d37c-4765-8890-90f629737b17>                                              |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:poweredge:cmc:syslog        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_poweredge_cmc      | dell:poweredge:cmc:syslog     | infraops          | none          |


## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-dell_cmc.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-dell_cmc[sc4s-vps] {
	filter { 
        host("test-dell-cmc-" type(string) flags(prefix))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('dell')
            product('poweredge_cmc')
        ); 
    };   
};
```