# EMC Powerswitch N Series

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Product Manual | <https://dl.dell.com/manuals/common/networking_nxxug_en-us.pdf>  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:emc:powerswitch:n        | None                                                                                               |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dellemc_powerswitch_n      | all       | netops          | none          |


## Parser Configuration
1. Through sc4s-vps
```c
#/opt/sc4s/local/config/app-parsers/app-vps-dell_switch_n.conf
#File name provided is a suggestion it must be globally unique

application app-vps-dell_switch_n[sc4s-vps] {
 filter { 
        host("test-dell-switch-n-" type(string) flags(prefix))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('dellemc')
            product('powerswitch_n')
        ); 
    };   
};
```

2. or through unique port
```
# /opt/sc4s/env_file 
SC4S_LISTEN_DELLEMC_POWERSWITCH_N_UDP_PORT=5005
```