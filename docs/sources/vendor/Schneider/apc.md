# APC Power systems

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                                  |
| Product Manual | multiple |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| apc:syslog  | None |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| schneider_apc      | apc:syslog     | main          | none          |


## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-schneider_apc.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-schneider_apc[sc4s-vps] {
	filter { 
        host("test_apc-*" type(glob))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('schneider')
            product('apc')
        ); 
    };   
};



```
