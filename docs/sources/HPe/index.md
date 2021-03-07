# Vendor - HPE

## Product - JetDirect


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| hpe:jetdirect | none |


### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| hpe_jetdirect     | print          | none          |

### Filter type

MSG Parse: This filter parses message content


### Options

Note listed for reference processing utilizes the Microsoft ArcSight log path as this format is a subtype of CEF

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_HPE_JETDIRECT_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_HPE_JETDIRECT_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_HPE_JETDIRECT | no | Enable archive to disk for this specific source |
| SC4S_DEST_HPE_JETDIRECT_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |



### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=hpe:jetdirect")
```


