# Terastation

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
| buffalo:terastation        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| buffalo_terastation      | buffalo:terastation       | infraops          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-buffalo_terastation.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-buffalo_terastation[sc4s-vps] {
 filter { 
        host("^test_buffalo_terastation-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('buffalo')
            product('terastation')
        ); 
    };   
};

```
