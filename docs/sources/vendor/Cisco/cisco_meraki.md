## Meraki (MR, MS, MX)

## Key facts
* Cisco Meraki messages are not distinctive, which means that it's impossible to parse the sourcetype based on the log message.
* Because of the above you should either configure known Cisco Meraki hosts in SC4S, or open unique ports for Cisco Meraki devices.
* [Splunk Add-on for Cisco Meraki 2.1.0](https://splunkbase.splunk.com/app/5580) doesn't support syslog. Use [TA-meraki](https://splunkbase.splunk.com/app/3018) instead. `TA-meraki 1.1.5` requires sourcetype `meraki`.


## Links
| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3018>                                                                 |
| Product Manual | <https://documentation.meraki.com/zGeneral_Administration/Monitoring_and_Reporting/Syslog_Server_Overview_and_Configuration> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| meraki:accesspoints        | Not compliant with the Splunk Add-on                                                            |
| meraki:securityappliances        | Not compliant with the Splunk Add-on                                                      |
| meraki:switches        | Not compliant with the Splunk Add-on                                                                |
| meraki        | For all Meraki devices. Compliant with the Splunk Add-on                                                                             |

## Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| meraki_accesspoints     | meraki:accesspoints    | netfw          |  |
| meraki_securityappliances     | meraki:securityappliances    | netfw          |  |
| meraki_switches     | meraki:switches    | netfw          |  |
| cisco_meraki | meraki | netfw |  |


## Parser Configuration
1. Either by defining Cisco Meraki hosts:
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
        host("^test-meraki-")
        or host("^test-mx-")
        or host("^test-mr-")
        or host("^test-ms-")
    };
    parser { app-vps-test-cisco_meraki(); };
};
```

2. Or by a unique port:
```
# /opt/sc4s/env_file
SC4S_LISTEN_CISCO_MERAKI_UDP_PORT=5004
SC4S_LISTEN_MERAKI_SECURITYAPPLIANCES_UDP_PORT=5005
SC4S_LISTEN_MERAKI_ACCESSPOINTS_UDP_PORT=5006
SC4S_LISTEN_MERAKI_SWITCHES_UDP_PORT=5007
```