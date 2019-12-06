# Vendor - Checkpoint

## Product - Log Exporter (Splunk)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4293/                                                                 |
| Product Manual | https://sc1.checkpoint.com/documents/App_for_Splunk/html_frameset.htm |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cp_log         | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_splunk         | cp_log         | netfw          | none           |

### Source and Index Configuration

Checkpoint Software blades with CIM mapping have been sub-grouped into sources
to allow routing to appropriate indexes. All other source meta data is left at default

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_splunk_dlp         | dlp         | netdlp          | none           |
| checkpoint_splunk_email         | email         | email          | none           |
| checkpoint_splunk_firewall         | firewall         | netfw          | none           |
| checkpoint_splunk_sessions         | sessions         | netops          | none           |
| checkpoint_splunk_web         | web         | netproxy          | none           |

### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Follow vendor configuration steps per Product Manual above 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CHECKPOINT_SPLUNK_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the port number defined |
| SC4S_LISTEN_CHECKPOINT_SPLUNK_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the port number defined |
| SC4S_ARCHIVE_CHECKPOINT_SPLUNK | no | Enable archive to text for this specific source |
| SC4S_DEST_CHECKPOINT_SPLUNK_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cp_log
```

Verify timestamp, and host values match as expected   
