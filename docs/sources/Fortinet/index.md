# Vendor - Fortinet

Fortinet uses incorrect descriptions for syslog destinations in their documentation (conflicting with RFC standard definitions).
When configuring a fortigate fortios device for TCP syslog, port 601 or an RFC6587 custom port must be used.
UDP syslog should use the default port of 514.

WARNING: Legacy Reliable (RFC3195) is not supported; this protocol is obsolete.

## Product - Fortigate

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2846/                                                                 |
| Product Manual | https://docs.fortinet.com/product/fortigate/6.2                                                         |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| fgt_log        | Catch-all sourcetype; not used by the TA                                                                |
| fgt_traffic    | None                                                                                                    |
| fgt_utm        | None                                                                                                    |
| fgt_event      | None                                                                                                    |


### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| fortinet_fortios_traffic      | fgt_traffic      | netfw          | none          |
| fortinet_fortios_utm    | fgt_utm      | netfw          | none          |
| fortinet_fortios_event    | fgt_event      | netops          | none          |
| fortinet_fortios_log    | fgt_log      | netops          | none          |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
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

### Options

* NOTE:  Remember to set the variable(s) below only _once_, regardless of how many unique ports and/or Fortinet device types
are in use.  See the introductory note above for more details.

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_FORTINET_RFC6587_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_FORTINET_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_FORTINET | no | Enable archive to disk for this specific source |
| SC4S_DEST_FORTINET_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_OPTION_FORTINET_SOURCETYPE_PREFIX | fgt | Notice starting with version 1.6 of the fortinet add-on and app the sourcetype required changes from `fgt_*` to `fortinet_*` this is a breaking change to use the new sourcetype set this variable to `fortigate` in the env_file |


### Verification

An active firewall will generate frequent events, in addition fortigate has the ability to test logging functionality using a built in command

```
diag log test
```

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=fgt_log OR sourcetype=fgt_traffic OR sourcetype=fgt_utm)
```

### UTM Message type

![FortiGate UTM message](FortiGate_utm.png)

### Traffic Message Type

![FortiGate Traffic message](FortiGate_traffic.png)

###Event Message Type
![FortiGate Event message](FortiGate_event.png)

Verify timestamp, and host values match as expected

## Product - FortiWeb

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4679/                                                                 |
| Product Manual | https://docs.fortinet.com/product/fortiweb/6.3                                                         |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| fgt_log        | Catch-all sourcetype; not used by the TA                                                                |
| fwb_traffic    | None                                                                                                    |
| fwb_attack     | None                                                                                                    |
| fwb_event      | None                                                                                                    |


### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| fortinet_fortiweb_traffic      | fwb_traffic      | netfw          | none          |
| fortinet_fortiweb_attack    | fwb_attack      | netids          | none          |
| fortinet_fortiweb_event    | fwb_event      | netops          | none          |
| fortinet_fortiweb_log    | fwb_log      | netops          | none          |


### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
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

### Options

* NOTE:  Remember to set the variable(s) below only _once_, regardless of how many unique ports and/or Fortinet device types
are in use.  See the introductory note above for more details.

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_FORTINET_TCP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_FORTINET_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_FORTINET | no | Enable archive to disk for this specific source |
| SC4S_DEST_FORTINET_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active firewall will generate frequent events, in addition fortigate has the ability to test logging functionality using a built in command

```
diag log test
```

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=fwb_log OR sourcetype=fwb_traffic OR sourcetype=fwb_attack OR sourcetype=fwb_event)
```

Verify timestamp, and host values match as expected
