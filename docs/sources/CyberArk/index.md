# Vendor - CyberArk

## Product - EPV

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CyberArk | https://splunkbase.splunk.com/app/2891/                                                              |
| Add-on Manual | https://docs.splunk.com/Documentation/AddOns/latest/CyberArk/About                                                      |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cyberark:epv:cef        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| CyberArk_Vault      | cyberark:epv:cef      | netauth          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=cef sourcetype="cyberark:epv:cef")
```

## Product - PTA

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CyberArk | https://splunkbase.splunk.com/app/2891/                                                              |
| Add-on Manual | https://docs.splunk.com/Documentation/AddOns/latest/CyberArk/About                                                      |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cyberark:pta:cef        | None                                                                                                |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Cyber-Ark_Vault      | cyberark:pta:cef      | main          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected    

```
index=<asconfigured> (sourcetype=cef sourcetype="cyberark:pta:cef")
```
