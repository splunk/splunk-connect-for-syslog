
# Firewall OS

Firewall OS format is by devices supporting a direct Syslog output
## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                                |
| Product Manual | unknown |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cp_log:fw:syslog         | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_fw         | cp_log:fw:syslog         | netops         | none           |

## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-checkpoint_fw.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-checkpoint_fw[sc4s-vps] {
	filter { 
        host("^checkpoint_fw-")
    };	
    parser { 
        p_set_netsource_fields(
            vendor('checkpoint')
            product('fw')
        ); 
    };   
};

```