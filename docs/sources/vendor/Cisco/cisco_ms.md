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
| cisco:ms     |  None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_ms    | cisco:ms    | netops          | None     |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-cisco_ms.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-cisco_ms[sc4s-vps] {
 filter { 
        host('^test-cms-')
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('cisco')
            product('ms')
        ); 
    };   
};


```
