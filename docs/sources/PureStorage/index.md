# Vendor - Pure Storage

## Product - Array

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None  note TA published on Splunk base does not include syslog extractions                                                                |
| Product Manual |  |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ossec     |  The add-on supports data from the following sources: File Integrity Management (FIM) data, FTP data, su data, ssh data, Windows data, including audit and logon information  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| purestorage_array    | purestorage:array    | infraops          | None     |
| purestorage_array_${class}    | purestorage:array:class    | infraops          | class is extracted as the string following "purity."     |

### Filter type

MSG Parsing

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Pure Storage Follow vendor configuration steps per Product Manual.
* Ensure host and timestamp are included.

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_PURESTORAGE_ARRAY_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_PURESTORAGE_ARRAY_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_PURESTORAGE_ARRAY | no | Enable archive to disk for this specific source |
| SC4S_DEST_PURESTORAGE_ARRAY_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=infraops sourcetype=purestorage:array*
```

Verify timestamp, and host values match as expected