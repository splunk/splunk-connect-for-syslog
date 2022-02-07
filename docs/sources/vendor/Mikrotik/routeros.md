# RouterOS

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514
* RouterOS will send ISC Bind and ISC DHCPD events

## Links


## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| routeros | none |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| mikrotik_routeros     | netops         | none          |
| mikrotik_routeros_fw     | netfw         | Used for events with forward:          |

## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-mikrotik_routeros.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-mikrotik_routeros[sc4s-vps] {
	filter { 
        host("test-mrtros-" type(string) flags(prefix))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('mikrotik')
            product('routeros')
        ); 
    };   
};

```
