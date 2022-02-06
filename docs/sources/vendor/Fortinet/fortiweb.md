# FortiWeb

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4679/>                                                                 |
| Product Manual | <https://docs.fortinet.com/product/fortiweb/6.3>                                                         |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| fgt_log        | Catch-all sourcetype; not used by the TA                                                                |
| fwb_traffic    | None                                                                                                    |
| fwb_attack     | None                                                                                                    |
| fwb_event      | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| fortinet_fortiweb_traffic      | fwb_traffic      | netfw          | none          |
| fortinet_fortiweb_attack    | fwb_attack      | netids          | none          |
| fortinet_fortiweb_event    | fwb_event      | netops          | none          |
| fortinet_fortiweb_log    | fwb_log      | netops          | none          |

## Source Setup and Configuration

* Refer to the admin manual for specific details of configuration to send Reliable syslog using RFC 3195 format, a typical logging configuration will include the following features.

```
config log syslog-policy

edit splunk  

config syslog-server-list 

edit 1

set server x.x.x.x

set port 514 (Example. Should be the same as default or dedicated port selected for sc4s)   

end

end

config log syslogd

set policy splunk

set status enable

end

```

