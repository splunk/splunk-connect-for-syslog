# RSA SecureID

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2958/>                                                                 |
| Product Manual | <https://docs.splunk.com/Documentation/AddOns/released/RSASecurID/Aboutthisaddon>  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| rsa:securid:syslog        | Catchall; used if a more specific source type can not be identified                                                                                                 |
| rsa:securid:admin:syslog    | None                                                                                         |
| rsa:securid:runtime:syslog     | None                                                               | rsa:securid:system:syslog     | None                                                                                          |
| nix:syslog     | None                                                                                          |

## Sourcetype and Index Configuration

| key                     | sourcetype     | index          | notes          |
|-------------------------|----------------|----------------|----------------|
| dell-rsa_secureid       | all       | netauth          | none          |
| dell-rsa_secureid_trace | rsa:securid:trace       | netauth          | none          |
| dell-rsa_secureid       | nix:syslog      | osnix          | uses os_nix key of not configured bye host/ip/port          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app_parsers/app-vps-dell_rsa_secureid.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-dell_rsa_secureid[sc4s-vps] {
 filter { 
        host("test_rsasecureid*" type(glob))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('dell')
            product('rsa_secureid')
        ); 
    };   
};
```
