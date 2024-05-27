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
| aruba:clearpass| Dynamically  Created                                                                                    |


### Index Configuration

| key                                     | index  | notes          |
|-----------------------------------------|--------|----------------|
| aruba_clearpass                         | netops | none           |
| aruba_clearpass_endpoint-profile        | netops | none           |
| aruba_clearpass_alert                   | netops | none           |
| aruba_clearpass_endpoint-audit-record   | netops | none           |
| aruba_clearpass_policy-server-session   | netops | none           |
| aruba_clearpass_post-auth-monit-config  | netops | none           |
| aruba_clearpass_snmp-session-log        | netops | none           |
| aruba_clearpass_radius-session          | netops | none           |
| aruba_clearpass_system-event            | netops | none           |
| aruba_clearpass_tacacs-accounting-detail| netops | none           |
| aruba_clearpass_tacacs-accounting-record| netops | none           |


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
