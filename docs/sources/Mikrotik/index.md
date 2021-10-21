# Vendor - Mikrotik

## Product - dns

This source type is often re-implemented by specific add-ons such as infoblox or bluecat if a more specific source type is desired
see that source documentation for instructions

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3845/                                              |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| routeros | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| mikrotik_routeros     | netops         | none          |
| mikrotik_routeros_fw     | netfw         | Used for events with forward:          |

### Filter type

Vendor Product by source configuration required

### Options

None



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=routeros")
```



## Product - DHCPD

This source type is often re-implemented by specific add-ons such as infoblox or bluecat if a more specific source type is desired
see that source documentation for instructions

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/3010/                                                   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| isc:dhcp | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| isc_dhcp     | isc:dhcp          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

None



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=isc:dhcp")
```

