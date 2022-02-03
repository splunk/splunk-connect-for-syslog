# Vendor - Ossec

## Product - Ossec

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2808/                                                                |
| Product Manual | https://www.ossec.net/docs/index.html |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ossec     |  The add-on supports data from the following sources: File Integrity Management (FIM) data, FTP data, su data, ssh data, Windows data, including audit and logon information  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ossec_ossec    | ossec    | main          | None     |

### Filter type

IP, Netmask or Host

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Ossec Follow vendor configuration steps per Product Manual.
* Ensure host and timestamp are included.
* Update ``vi /opt/sc4s/local/context/vendor_product_by_source.conf `` update the host or ip mask for ``f_ossec`` to identiy the ossec events.

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_OSSEC_OSSEC_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_OSSEC_OSSEC_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_OSSEC_OSSEC | no | Enable archive to disk for this specific source |
| SC4S_DEST_OSSEC_OSSEC_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=main sourcetype=ossec
```

Verify timestamp, and host values match as expected