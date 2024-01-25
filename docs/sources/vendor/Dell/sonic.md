# Dell Networking SONiC

## Key facts
* Requires vendor product by source configuration

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Product Manual | [link](https://www.dell.com/support/kbdoc/en-us/000215519/dell-networking-sonic-system-log-messages-and-audit-logs#:~:text=They%20include%20events%20such%20as,classified%20based%20on%20severity%20level)  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| dell:sonic        | None                                                                                               |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| dell_sonic      | dell:sonic       | netops          | none          |


## Parser Configuration
1. Through sc4s-vps
```c
#/opt/sc4s/local/config/app-parsers/app-vps-dell_sonic.conf
#File name provided is a suggestion it must be globally unique

application app-vps-dell_sonic[sc4s-vps] {
 filter { 
        host("sonic" type(string) flags(prefix))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('dell')
            product('sonic')
        ); 
    };   
};
```

2. or through unique port
```
# /opt/sc4s/env_file 
SC4S_LISTEN_DELL_SONIC_UDP_PORT=5005
```