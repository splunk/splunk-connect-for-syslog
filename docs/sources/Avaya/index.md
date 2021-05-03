# Vendor - Avaya


## Product - Avaya Sip Manager

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| avaya:avaya        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| avaya_sipmgr      | avaya:avaya       | main          | none          |

### Filter type

This filter uses msg parsgin.

### Setup and Configuration

The source device send non compliant syslog format (legacy bsd based) with embeded new line and no IETF frames this source must
 be configured to use UDP protocol.

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_AVAYA_SIPMGR_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=avaya:sipmgr| stats count by host
```
