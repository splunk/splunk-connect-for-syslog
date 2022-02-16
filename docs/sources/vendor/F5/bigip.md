# BigIP

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2680/>                                                                 |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| f5:bigip:syslog        | None                                                                                                    |
| f5:bigip:irule    | None                                                                                         |
| f5:bigip:ltm:http:irule | None |
| f5:bigip:gtm:dns:request:irule | None |
| f5:bigip:gtm:dns:response:irule | None |
| f5:bigip:ltm:failed:irule | None |
| f5:bigip:asm:syslog | None |
| f5:bigip:apm:syslog | None |
| nix:syslog     | None                                                                                          |
| f5:bigip:ltm:access_json | User defined configuration via irule producing a RFC5424 syslog event with json content within the message field `<111>1 2020-05-28T22:48:15Z foo.example.com F5 - access_json - {"event_type":"HTTP_REQUEST", "src_ip":"10.66.98.41"}` This source type requires a customer specific Splunk Add-on for utility value |

### Index Configuration

| key            | index          | notes          |
|----------------|----------------|----------------|
| f5_bigip       | netops          | none          |
| f5_bigip_irule | netops          | none          |
| f5_bigip_asm   | netwaf          | none          |
| f5_bigip_apm   | netops          | none          |
| f5_bigip_nix   | netops          | if `f_f5_bigip` is not set the index osnix will be used          |
| f5_bigip_access_json | netops | none |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-f5_bigip.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-f5_bigip[sc4s-vps] {
 filter { 
        "${HOST}" eq "f5_bigip"
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('f5')
            product('bigip')
        ); 
    };   
};

```
