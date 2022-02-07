# Web Appliance

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
| sophos:webappliance        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| sophos_webappliance        | sophos:webappliance         | netproxy          | none          |


## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-sophos_webappliance.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-sophos_webappliance[sc4s-vps] {
	filter { 
        host("test-sophos-webapp-" type(string) flags(prefix))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('sophos')
            product('webappliance')
        ); 
    };   
};


```
