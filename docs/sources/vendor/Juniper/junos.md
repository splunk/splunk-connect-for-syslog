# JunOS

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | <https://splunkbase.splunk.com/app/2847/>                                 |
| JunOS TechLibrary | <https://www.juniper.net/documentation/en_US/junos/topics/example/syslog-messages-configuring-qfx-series.html> |

## Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| juniper:junos:firewall   | None                                                             |
| juniper:junos:firewall:structured   | None                                                             |
| juniper:junos:idp   | None                                                             |
| juniper:junos:idp:structured   | None                                                             |
| juniper:junos:aamw:structured   | None                                                             |
| juniper:junos:secintel:structured   | None                                                             |
| juniper:junos:snmp   | None                                                             |

## Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| juniper_junos_flow         | juniper:junos:firewall | netfw          | none          |
| juniper_junos_idp          | juniper:junos:idp      | netids         | none          |
| juniper_junos_utm          | juniper:junos:firewall | netfw          | none          |

