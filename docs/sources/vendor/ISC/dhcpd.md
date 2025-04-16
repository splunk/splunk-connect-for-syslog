
# dhcpd

This source type is often re-implemented by specific add-ons such as infoblox or bluecat if a more specific source type is desired
see that source documentation for instructions

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3010/>                                                   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| isc:dhcpd | none |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| isc_dhcpd     | netipam          | none          |

### Filter type

MSG Parse: This filter parses message content

## Options

None

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected

```
index=<asconfigured> (sourcetype=isc:dhcpd")
```
