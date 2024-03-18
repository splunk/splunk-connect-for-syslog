## Meraki (MR, MS, MX)

## Key facts
* Cisco Meraki messages are not distinctive, which means that it's impossible to parse the sourcetype based on the log message.
* Because of the above you should either configure known Cisco Meraki hosts in SC4S, or open unique ports for Cisco Meraki devices.
* Before reading this document see [Cisco Meraki syslog overview and configuration](https://documentation.meraki.com/General_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration).

## Links
| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/5580>                                                                 |
| Product Manual | <https://documentation.meraki.com/zGeneral_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| meraki:accesspoints        | None                                                                                             |
| meraki:securityappliances        | None                                                                                             |
| meraki:switches        | None                                                                                             |
| meraki        | None                                                                                             |

## Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_meraki_accesspoints     | meraki:accesspoints    | netfw          |  |
| cisco_meraki_securityappliances     | meraki:securityappliances    | netfw          |  |
| cisco_meraki_switches     | meraki:switches    | netfw          |  |
| cisco_meraki | meraki | netfw |  |


## Parser Configuration
1. Either by defining all Cisco Meraki hosts in SC4S
```c
#/opt/sc4s/local/config/app_parsers/app-vps-cisco_meraki.conf
#File name provided is a suggestion it must be globally unique

block parser app-vps-test-cisco_meraki() {
    channel {
        if {
            filter { host("^test-mx-") };
            parser { 
                p_set_netsource_fields(
                    vendor('meraki')
                    product('securityappliances')
                ); 
            };
        } elif {
            filter { host("^test-mr-") };
            parser { 
                p_set_netsource_fields(
                    vendor('meraki')
                    product('accesspoints')
                ); 
            };
        } elif {
            filter { host("^test-ms-") };
            parser { 
                p_set_netsource_fields(
                    vendor('meraki')
                    product('switches')
                ); 
            };
        } else {
            parser { 
                p_set_netsource_fields(
                    vendor('cisco')
                    product('meraki')
                ); 
            };
        };
    }; 
};


application app-vps-test-cisco_meraki[sc4s-vps] {
    filter {
        host("^test-")
        or host("^test-mx-")
        or host("^test-mr-")
        or host("^test-ms-")
    };
    parser { app-vps-test-cisco_meraki(); };
};
```

2. Or by unique port
```
# /opt/sc4s/env_file
SC4S_LISTEN_CISCO_MERAKI_UDP_PORT=5004
SC4S_LISTEN_CISCO_MERAKI-SECURITYAPPLIANCES_UDP_PORT=5005
SC4S_LISTEN_CISCO_MERAKI-ACCESSPOINTS_UDP_PORT=5006
SC4S_LISTEN_CISCO_MERAKI-SWITCHES_UDP_PORT=5007
```

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_DEST_CISCO_MERAKI-SECURITYAPPLIANCES_SPLUNK_HEC_FMT | JSON | Restructure data from vendor format to json for splunk destinations set to "NONE" for native format |
| SC4S_DEST_CISCO_MERAKI-ACCESSPOINTS_SPLUNK_HEC_FMT | JSON | Restructure data from vendor format to json for splunk destinations set to "NONE" for native format |
| SC4S_DEST_CISCO_MERAKI-SWITCHES_SPLUNK_HEC_FMT | JSON | Restructure data from vendor format to json for splunk destinations set to "NONE" for native format |