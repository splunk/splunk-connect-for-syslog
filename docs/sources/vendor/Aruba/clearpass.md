# Clearpass

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| aruba:clearpass | Dynamically  Created |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| aruba_clearpass     | print          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-aruba_clearpass.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-aruba_clearpass[sc4s-vps] {
 filter { 
        host("aruba-cp-*" type(glob))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('aruba')
            product('clearpass')
        ); 
    };   
};


```
