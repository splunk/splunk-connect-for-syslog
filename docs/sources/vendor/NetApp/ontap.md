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
| netapp:ontap:audit  | None |
| netapp:ontap:ems  | None |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| netapp_ontap_audit      | netapp:ontap:audit     | infraops          | none          |
| netapp_ontap_ems      | netapp:ontap:ems     | infraops          | none          |


## Parser Configuration
1. Through sc4s-vps
```c
#/opt/sc4s/local/config/app-parsers/app-vps-netapp_ontap.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-netapp_ontap[sc4s-vps] {
    filter { 
        host("netapp-ontap-" type(string) flags(prefix))
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