# Unifi

All Ubiquity Unfi firewalls, switches, and access points share a common syslog configuration via the NMS.

* Login to NMS
* Navigate to settings
* Navigate to Site
* Enable Remote syslog server
* Enter hostname and port

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4107/>                                                                 |
| Product Manual | <https://https://help.ubnt.com/>    |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ubnt  | Used when no sub source type is required by add on |
| ubnt:fw  | USG events |
| ubnt:threat | USG IDS events    |
| ubnt:switch  | Unifi Switches |
| ubnt:wireless  | Access Point logs |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ubiquiti_unifi      | ubnt     | netops          | none          |
| ubiquiti_unifi_fw      | ubnt:fw       | netfw          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-ubiquiti_unifi_fw.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-ubiquiti_unifi_fw[sc4s-vps] {
	filter { 
        host("usg-*" type(glob))
    };	
    parser { 
        p_set_netsource_fields(
            vendor('ubiquiti')
            product('unifi')
        ); 
    };   
};

```
