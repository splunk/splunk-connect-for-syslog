## Product - GitHub Enterprise Server

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  |                                                                 |
| Product Manual |  |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| github:enterprise:audit     |  The audit logs of GitHub Enterprise server have information about audites actions performed by github user.  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| github    | github:enterprise:audit    | github          | None     |

### Filter type

IP, Netmask or Host

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* GitHub Follow vendor configuration steps per Product Manual.
* Ensure host and timestamp are included.
* Update ``vi /opt/sc4s/local/context/vendor_product_by_source.conf `` update the host or ip mask for ``f_github`` to identiy the github events.

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_GITHUB_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_GITHUB_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_GITHUB | no | Enable archive to disk for this specific source |
| SC4S_DEST_GITHUB_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=github sourcetype=github:enterprise:audit
```

Verify timestamp, and host values match as expected