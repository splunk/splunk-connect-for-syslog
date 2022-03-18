# FortiWMail

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                               |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| fwb:email:<type>          | type value is determined from the message                                                               |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| fortinet_fortimail_<type>      | fwb:email:<type>      | email          |  type value is determined from the message          |

## Source Setup and Configuration

* Refer to the admin manual for specific details of configuration to send Reliable syslog using RFC 3195 format, a typical logging configuration will include the following features.

```
config log memory filter

set forward-traffic enable

set local-traffic enable

set sniffer-traffic disable

set anomaly enable

set voip disable

set multicast-traffic enable

set dns enable

end

config system global

set cli-audit-log enable

end

config log setting

set neighbor-event enable

end

```

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX | fgt | Notice starting with version 1.6 of the fortinet add-on and app the sourcetype required changes from `fgt_*` to `fortinet_*` this is a breaking change to use the new sourcetype set this variable to `fortigate` in the env_file |

