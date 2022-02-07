# NTP Appliance

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| spectracom:ntp        | None                                                                                                    |
| nix:syslog | None |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| spectracom_ntp      | spectracom:ntp       | netops          | none          |


## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-spectracom_ntp.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-spectracom_ntp[sc4s-vps] {
	filter { 
        netmask(169.254.100.1/24)
    };	
    parser { 
        p_set_netsource_fields(
            vendor('spectracom')
            product('ntp')
        ); 
    };   
};

```
