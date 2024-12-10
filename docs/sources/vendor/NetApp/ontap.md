#  OnTap

## Key facts

* MSG Format based filter
* Netapp Ontap messages are not distinctive. So, either configure known Netapp Ontap hosts in SC4S, or open unique ports for Netapp Ontap devices

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3418/>                                                  |
| Product Manual | unknown |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ontap:ems  | This sourcetype will be assinged only when the environment variable `SC4S_NETAPP_ONTAP_NEW_FORMAT` is not set or is set to 'no'. By default it is unset |
| netapp:ontap:audit  | This sourcetype will be assinged only when the environment variable `SC4S_NETAPP_ONTAP_NEW_FORMAT` is set to 'yes' |
| netapp:ontap:ems  | This sourcetype will be assinged only when the environment variable `SC4S_NETAPP_ONTAP_NEW_FORMAT` is set to 'yes' |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| netapp_ontap      | ontap:ems     | infraops          | none          |
| netapp_ontap_audit      | netapp:ontap:audit     | infraops          | none          |
| netapp_ontap_ems      | netapp:ontap:ems     | infraops          | none          |

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_NETAPP_ONTAP_NEW_FORMAT      | empty string      | (empty/yes) Set to "yes" for the applying the latest changes. Make sure to configure your system to send the logs to a specific port or have a hostname-based configuration |

## Parser Configuration
1. Through sc4s-vps
```c
#/opt/sc4s/local/config/app-parsers/app-vps-netapp_ontap.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-netapp_ontap[sc4s-vps] {
    filter {
        host("netapp-ontap-" type(string) flags(prefix))
        or (
            message("netapp-ontap-" type(string) flags(prefix))
            and program("netapp-ontap-" type(string) flags(prefix))
        )
    };
    parser {
        p_set_netsource_fields(
            vendor('netapp')
            product('ontap')
        );
    };
};
```

2. or through unique port
```
# /opt/sc4s/env_file 
SC4S_LISTEN_NETAPP_ONTAP_UDP_PORT=5005
```