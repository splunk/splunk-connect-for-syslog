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
| checkpoint_splunk         | cp_log         | netops         | none           |

### Source and Index Configuration

Checkpoint Software blades with CIM mapping have been sub-grouped into sources
to allow routing to appropriate indexes. All other source meta data is left at default

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_splunk_dlp         | dlp         | netdlp          | none           |
| checkpoint_splunk_email         | email         | email          | none           |
| checkpoint_splunk_firewall         | firewall         | netfw          | none           |
| checkpoint_splunk_os | program:${program} | netops | none |
| checkpoint_splunk_sessions         | sessions         | netops          | none           |
| checkpoint_splunk_web         | web         | netproxy          | none           |
| checkpoint_splunk_audit | audit | netops | none |
| checkpoint_splunk_endpoint | endpoint | netops | none |
| checkpoint_splunk_network | network | netops |
| checkpoint_splunk_ids | ids | netids |
| checkpoint_splunk_ids_malware | ids_malware | netids |


### Filter type

MSG Parse: This filter parses message content

The Splunk `host` field will be derived as follows using the first match

* Use the hostname field 
* Use the first CN component of origin_sic_name/originsicname
* If host is not set from CN use the `hostname` field
* If host is not set use the BSD syslog header host

If the host is in the format `<host>-v_<bladename>` use `bladename` for host


### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Follow vendor configuration steps per Product Manual above 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CHECKPOINT_SPLUNK_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the port number defined |
| SC4S_LISTEN_CHECKPOINT_SPLUNK_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the port number defined |
| SC4S_ARCHIVE_CHECKPOINT_SPLUNK | no | Enable archive to disk for this specific source |
| SC4S_DEST_CHECKPOINT_SPLUNK_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL | no | Suppress any duplicate product+loguid pairs processed within 2 seconds of the last matching event |
| SC4S_LISTEN_CHECKPOINT_SPLUNK_OLD_HOST_RULES | empty string | when set to `yes` reverts host name selection order to originsicname-->origin_sic_name-->hostname |

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cp_log
```

Verify timestamp, and host values match as expected

## Product - Log Exporter (Syslog)

* This is an alpha release not for production use.
* The syslog format from the log_exporter is the recommended format to collect checkpoint logs as it is more performant and efficient than its other default formats.

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  |                                                                       |
| Product Manual | https://sc1.checkpoint.com/documents/App_for_Splunk/html_frameset.htm |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cp_log:syslog  | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_splunk         | cp_log:syslog         | netops          | none           |

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
| checkpoint_splunk_audit         | audit         | netops         | none         |
| checkpoint_splunk_endpoint         | endpoint         | netops         | none         |
| checkpoint_splunk_network         | network         | netops         |
| checkpoint_splunk_ids | ids | netids |
| checkpoint_splunk_ids_malware | ids_malware | netids |

### Filter type

MSG Parse: This filter parses message content

### Setup and Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* To configure the valid syslog format in Checkpoint, follow the steps below 
* Go to the cp terminal
* Enter expert command for login in expert mode
* Enter cd $EXPORTERDIR
* In this directory check targets if it's empty then configure a new target for the logs with help of below command
* cp_log_export add name <your_log_exporter> target-server <target-server IP address> target-port <target-port> protocol <(udp|tcp)> format <(syslog)|(cef)|(splunk)(generic)>
* Then navigate to conf directory
* Execute cp SyslogFormatDefination.xml SplunkRecommendedFormatDefinition.xml
* Open SplunkRecommendedFormatDefinition.xml in edit mode and modify the start_message_body,fields_seperatator,field_value_seperatator as shown below.
``` 
<start_message_body>[sc4s@2620 </start_message_body>
```
```
<fields_seperatator> </fields_seperatator>
```
```
<field_value_seperatator>=</field_value_seperatator>
```
* Copy SplunkRecommendedFormatDefinition.xml into $EXPORTERDIR/targets/<your_log_exporter>/conf
* Navigate to the configuration file $EXPORTERDIR/targets/<your_log_exporter>/targetConfiguration.xml and open it in edit mode.
* Add the reference to the SplunkRecommendedFormatDefinition.xml under the key <formatHeaderFile>. For example, if $EXPORTERDIR=/opt/CPrt-R81/log_exporter, the absolute path will become:  
```
<formatHeaderFile>/opt/CPrt-R81/log_exporter/targets/<your_log_exporter>/conf/SplunkRecommendedFormatDefinition.xml</formatHeaderFile>
```
* Restart cp_log_exporter by executing the command cp_log_export restart name <your_log_exporter>

* Warning: Make sure if you migrating to different format, the earlier format is disabled or else it would lead to data duplication.


### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CHECKPOINT_SYSLOG_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the port number defined |
| SC4S_LISTEN_CHECKPOINT_SYSLOG_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the port number defined |
| SC4S_ARCHIVE_CHECKPOINT_SYSLOG | no | Enable archive to disk for this specific source |
| SC4S_DEST_CHECKPOINT_SYSLOG_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cp_log:syslog
```

Verify timestamp, and host values match as expected

## Product - Firewall OS 

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                                |
| Product Manual | unknown |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cp_log:fw:syslog         | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_fw         | cp_log:fw:syslog         | netops         | none           |


### Filter type

Custom port or vendor_product_by_source configuration required

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CHECKPOINT_FW_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the port number defined |
| SC4S_LISTEN_CHECKPOINT_FW_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the port number defined |
| SC4S_ARCHIVE_CHECKPOINT_FW | no | Enable archive to disk for this specific source |
| SC4S_DEST_CHECKPOINT_FW_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

Use the following search to validate events are present

```
index=<asconfigured> sourcetype=cp_log:fw:syslog