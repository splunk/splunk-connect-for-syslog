# Communications Management Controller

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
| cisco:cmc     |  None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_cmc    | cisco:cmc    | netops          | None     |


## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-cisco_cmc.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-cisco_cmc[sc4s-vps] {
	filter { 
        host('^test-ccmc-')
    };	
    parser { 
        p_set_netsource_fields(
            vendor('cisco')
            product('cmc')
        ); 
    };   
};


```