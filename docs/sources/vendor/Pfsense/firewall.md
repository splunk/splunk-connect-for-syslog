# Firewall

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/1527/>                                                                 |
| Product Manual | <https://docs.netgate.com/pfsense/en/latest/monitoring/copying-logs-to-a-remote-host-with-syslog.html?highlight=syslog> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| pfsense:filterlog  | None |
| pfsense:* | All programs other than filterlog |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| pfsense      | pfsense     | netops          | none          |
| pfsense_filterlog      | pfsense:filterlog      | netfw          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-pfsense_firewall.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-pfsense_firewall[sc4s-vps] {
 filter { 
        "${HOST}" eq "pfsense_firewall"
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('pfsense')
            product('firewall')
        ); 
    };   
};


```
