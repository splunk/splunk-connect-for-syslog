# Vendor - IBM

## Product - Data power

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4662/                                                      |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ibm:datapower:syslog        | Common sourcetype                                                                                                 |
| ibm:datapower:*        | * is taken from the event sourcetype                                                                                                 |
                                |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ibm_datapower      | na     | inifraops          | none          |

### Filter type

Requires dedicated port or vendor_product_by_source configuration

### Options


| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_IBM_DATAPOWER_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_IBM_DATAPOWER_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_IBM_DATAPOWER | no | Enable archive to disk for this specific source |
| SC4S_DEST_IBM_DATAPOWER_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |


### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected

```
index=<asconfigured> (sourcetype=cef source="ibm:datapower*")
```
