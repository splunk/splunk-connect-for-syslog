# Vendor - Pulse

## Product - Secure Connect

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | https://splunkbase.splunk.com/app/3852/                                 |
| JunOS TechLibrary | https://docs.pulsesecure.net/WebHelp/Content/PCS/PCS_AdminGuide_8.2/Configuring%20Syslog.htm |

### Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| pulse:connectsecure  | None                                                             |
| pulse:connectsecure:web   | None                                                             |

### Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| pulse_connect_secure         | pulse:connectsecure | netfw          | none          |
| pulse_connect_secure_web          | pulse:connectsecure:web      | netproxy         | none          |

### Filter type

* MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index as required.
* Follow vendor configuration steps per referenced Product Manual

### Options
Note RFC6587 framing is not supported over TLS at this time

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_PULSE_CONNECT_SECURE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers using legacy 3164 format|
| SC4S_LISTEN_PULSE_CONNECT_SECURE_RFC6587_PORT      | empty string      | Enable a TCP using IETF Framing (RFC6587) port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_PULSE_CONNECT_SECURE | no | Enable archive to disk for this specific source |
| SC4S_DEST_PULSE_CONNECT_SECURE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=pulse:connectsecure* | stats count by host
```

Verify the timestamp and host values match as expected

