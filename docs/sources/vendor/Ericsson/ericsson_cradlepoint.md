# Access Points

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|

## Sourcetypes

| sourcetype           | notes                                                                                                   |
|----------------------|---------------------------------------------------------------------------------------------------------|
| ericsson:cradlepoint | Dynamically  Created |

### Index Configuration

| key                  | index      | notes          |
|----------------------|------------|----------------|
| ericsson_cradlepoint | netops          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-ericsson_cradlepoint.conf
#File name provided is a suggestion it must be globally unique

application app-vps-ericsson_cradlepoint[sc4s-vps] {
    filter { 
        host("ericsson-cradlepoint_*" type(glob))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('ericsson')
            product('cradlepoint')
        ); 
    };   
};
```
