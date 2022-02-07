# DSX

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                     |
| Product Manual | <https://www.raritan.com/products/kvm-serial/serial-console-servers/serial-over-ip-console-server> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| raritan:dsx  | Note events do not contain host |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| raritan_dsx      | raritan:dsx     | infraops          | none          |



## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-raritan_dsx.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-raritan_dsx[sc4s-vps] {
	filter { 
        host("raritan_dsx*" type(glob))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('raritan')
            product('dsx')
        ); 
    };   
};


```
