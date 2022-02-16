# Access Points

## Key facts

* MSG Format based filter (Partial)
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| aruba:syslog | Dynamically  Created |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| aruba_ap     | netops          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-aruba_ap.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-aruba_ap[sc4s-vps] {
 filter { 
        host("aruba-ap-*" type(glob))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('aruba')
            product('ap')
        ); 
    };   
};
```
