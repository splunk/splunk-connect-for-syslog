# WAF (Cloud)

## Key facts

* MSG Format based filter
* RFC 5424 Framed


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                               |
| Product Manual | https://campus.barracuda.com/product/WAAS/doc/79462622/log-export |

## Sourcetypes

| sourcetype      | notes                                                                                                   |
|-----------------|---------------------------------------------------------------------------------------------------------|
|barracuda:tr   |  none  |

## Sourcetype and Index Configuration

| key    | sourcetype     | index  | notes          |
|--------|----------------|--------|----------------|
| barracuda_waf       |  barracuda:web:firewall  | netwaf  | None     |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-barracuda_syslog.conf
#File name provided is a suggestion it must be globally unique

application app-vps-barracuda_syslog[sc4s-vps] {
 filter {      
        netmask(169.254.100.1/24)
        or host("barracuda" type(string) flags(ignore-case))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('barracuda')
            product('syslog')
        ); 
    };   
};
```
