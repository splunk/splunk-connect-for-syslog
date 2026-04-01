# Silverpeak

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|

## Sourcetypes

| sourcetype       | notes |
|------------------|-------|
| aruba:silverpeak |       |    


### Index Configuration

| key                                      | index  | notes          |
|------------------------------------------|--------|----------------|
| aruba_silverpeak                         | netops | none           |


## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-aruba_silverpeak.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-aruba_silverpeak[sc4s-vps] {
 filter {
        host("silverpeak-" type(string) flags(prefix))
    };
    parser {
        p_set_netsource_fields(
            vendor('aruba')
            product('silverpeak')
        );
    };
};
```
