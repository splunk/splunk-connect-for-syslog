# Barracuda WAF (On Premises)

## Key facts

* RFC 5424 Framed with non-standard ISO timestamp: `%Y-%m-%d %H:%M:%S.%f %z`
* MSG Format based filter


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3776                                                               |
| Product Manual | https://campus.barracuda.com/product/webapplicationfirewall/doc/92767349/exporting-log-formats/ |

## Sourcetypes

| sourcetype      | notes                                                                                                   |
|-----------------|---------------------------------------------------------------------------------------------------------|
|barracuda:system   |  program("SYS")  |
|barracuda:waf   |  program("WF")  |
|barracuda:web   |  program("TR")  |
|barracuda:audit   |  program("AUDIT")  |
|barracuda:firewall   |  program("NF")  |

## Sourcetype and Index Configuration

| key    | sourcetype     | index  | notes          |
|--------|----------------|--------|----------------|
| barracuda_system       |  barracuda:system  | netwaf  | None     |
| barracuda_waf       |  barracuda:waf  | netwaf  | None     |
| barracuda_web       |  barracuda:web  | netwaf  | None     |
| barracuda_audit       |  barracuda:audit  | netwaf  | None     |
| barracuda_firewall       |  barracuda:firewall  | netwaf  | None     |