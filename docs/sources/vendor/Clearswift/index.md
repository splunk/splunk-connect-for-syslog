# WAF (Cloud)

## Key facts

* MSG Format based filter
* RFC 5424 Framed


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                               |
| Product Manual | https://hstechdocs.helpsystems.com/manuals/clearswift/seg/english/5_5_0/SEG_Install_Guide(en).pdf |

## Sourcetypes

| sourcetype              | notes                                                                                                   |
|-------------------------|---------------------------------------------------------------------------------------------------------|
| `clearswift:${PROGRAM}` |  none  |

## Sourcetype and Index Configuration

| key        | sourcetype     | index | notes          |
|------------|----------------|-------|----------------|
| clearswift |  `clearswift:${PROGRAM}` | email | None     |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-clearswift.conf
#File name provided is a suggestion it must be globally unique

application app-vps-clearswift[sc4s-vps] {
	filter {
        host("test-clearswift-" type(string) flags(prefix))
    };
    parser {
        p_set_netsource_fields(
            vendor('clearswift')
            product('clearswift')
        );
    };
};