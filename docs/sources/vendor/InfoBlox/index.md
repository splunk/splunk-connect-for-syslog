# NIOS

Warning: Despite the TA indication this data source is CIM compliant all versions of NIOS including the most recent available as of 2019-12-17 do not support the DNS data model correctly. For DNS security use cases use Splunk Stream instead.

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2934/>                                                                 |
| Product Manual | <https://docs.infoblox.com/display/ILP/NIOS?preview=/8945695/43728387/NIOS_8.4_Admin_Guide.pdf>   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| infoblox:dns        | None                                                                                                    |
| infoblox:dhcp    | None                                                                                         |
| infoblox:threat     | None                                                                                          |
| nix:syslog     | None                                                                                          |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| infoblox_nios_dns      | infoblox:dns       | netdns          | none          |
| infoblox_nios_dhcp    | infoblox:dhcp      | netipam          | none          |
| infoblox_nios_threat    | infoblox:threatprotect      | netids          | none          |
| infoblox_nios_audit    | infoblox:audit      | netops          | none          |
| infoblox_nios_fallback    | infoblox:port      | netops          | none          |


## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-infoblox_nios.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-infoblox_nios[sc4s-vps] {
	filter { 
        host("infoblox-*" type(glob))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('infoblox')
            product('nios')
        ); 
    };   
};


```
