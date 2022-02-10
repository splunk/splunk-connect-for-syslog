# Bastion

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3661/>                                                                 |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| WB:syslog  | note this sourcetype includes program:rdproxy all other data will be treated as nix  |

## Sourcetype and Index Configuration

| key                 | sourcetype             | index    | notes   |
|---------------------|------------------------|----------|---------|
| wallix_bastion     | infraops      | main     | none    |

## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-wallix_bastion.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-wallix_bastion[sc4s-vps] {
	filter { 
        host('^wasb')
    };	
    parser { 
        p_set_netsource_fields(
            vendor('wallix')
            product('bastion')
        ); 
    };   
};

```
