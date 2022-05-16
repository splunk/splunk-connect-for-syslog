# Switch

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Product - Switches

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| brocade:syslog        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| brocade_syslog      | brocade:syslog       | netops          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app_parsers/app-vps-brocade_syslog.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-brocade_syslog[sc4s-vps] {
 filter { 
        host("^test_brocade-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('brocade')
            product('syslog')
        ); 
    };   
};

```
