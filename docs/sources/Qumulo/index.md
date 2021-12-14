# Vendor - Qumulo

## Product - Storage

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | none                              |

### Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| qumulo:storage  | None                                                             |

### Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| qumulo_storage         | qumulo:storage | infraops          | none          |

### Filter type

* MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index as required.
* Follow vendor configuration steps per referenced Product Manual

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_QUMULO_STORAGE_TCP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers using legacy 3164 format|
| SC4S_ARCHIVE_QUMULO_STORAGE | no | Enable archive to disk for this specific source |
| SC4S_DEST_QUMULO_STORAGE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=qumulo:storage* | stats count by host
```

Verify the timestamp and host values match as expected

