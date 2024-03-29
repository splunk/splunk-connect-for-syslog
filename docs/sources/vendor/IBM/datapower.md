# Data power

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4662/>                                                      |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ibm:datapower:syslog        | Common sourcetype                                                                                                 |
| ibm:datapower:*        | * is taken from the event sourcetype                                                                                                 |
                                |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ibm_datapower      | na     | inifraops          | none          |

## Parser Configuration

Parser configuration is conditional only required if additional events are produced by the device that do not match the default configuration.

```c
#/opt/sc4s/local/config/app-parsers/app-vps-ibm_datapower.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-ibm_datapower[sc4s-vps] {
 filter { 
        host("^test-ibmdp-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('ibm')
            product('datapower')
        ); 
    };   
};

```
