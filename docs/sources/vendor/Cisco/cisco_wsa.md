# Web Security Appliance (WSA)

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/1747/>                                                                 |
| Product Manual | <https://www.cisco.com/c/en/us/td/docs/security/wsa/wsa11-7/user_guide/b_WSA_UserGuide_11_7.html> |


## Sourcetypes

| cisco:wsa:l4tm      | The L4TM logs of Cisco IronPort WSA record sites added to the L4TM block and allow lists.                                                                                                    |
| cisco:wsa:squid      | The access logs of Cisco IronPort WSA version prior to 11.7 record Web Proxy client history in squid.                                                                                           |
| cisco:wsa:squid:new     | The access logs of Cisco IronPort WSA version since 11.7 record Web Proxy client history in squid.                                                                                           |
| cisco:wsa:w3c:recommended     | The access logs of Cisco IronPort WSA version since 12.5 record Web Proxy client history in W3C.                                                                                           |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_wsa    | cisco:wsa:l4tm    | netproxy          | None     |
| cisco_wsa    | cisco:wsa:squid    | netproxy          | None     |
| cisco_wsa    | cisco:wsa:squid:new    | netproxy          | None     |
| cisco_wsa    | cisco:wsa:w3c:recommended    | netproxy          | None     |

### Filter type

IP, Netmask or Host

## Source Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* WSA Follow vendor configuration steps per Product Manual.
* Ensure host and timestamp are included.

## Parser Configuration

```c
#/opt/sc4s/local/app-parsers/app-vps-cisco_wsa.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-cisco_wsa[sc4s-vps] {
	filter { 
        host("^wsa-")
    };	
    parser { 
        p_set_netsource_fields(
            vendor('cisco')
            product('wsa')
        ); 
    };   
};
```