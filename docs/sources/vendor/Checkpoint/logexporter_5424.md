# Log Exporter (Syslog)

## Key Facts

* As of 2/1/2022 The Log Exporter configuration provided by CheckPoint is defective and produces invalid data the configuration below is REQUIRED
* MSG Format based filter
* RFC5424 without frame use port 514 TCP

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  |                                                                       |
| Product Manual | <https://sc1.checkpoint.com/documents/App_for_Splunk/html_frameset.htm> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cp_log:syslog  | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_splunk         | cp_log:syslog         | netops          | none           |

## Source and Index Configuration

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

## Source Configuration

* Install the Splunk Add-on on the search head(s) for the user communities interested in this data source. If SC4S is exclusively used the addon is not required on the indexer.
* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* To configure the valid syslog format in Checkpoint, follow the steps below
* Go to the cp terminal
* Enter expert command for login in expert mode
* Enter cd $EXPORTERDIR
* Then navigate to conf directory
* Execute cp SyslogFormatDefination.xml SplunkRecommendedFormatDefinition.xml
* Open SplunkRecommendedFormatDefinition.xml in edit mode and modify the start_message_body,fields_seperatator,field_value_seperatator as shown below.

```xml
<start_message_body>[sc4s@2620 </start_message_body>
```

```xml
<fields_seperatator> </fields_seperatator>
```

```xml
<field_value_seperatator>=</field_value_seperatator>
```

* Copy SplunkRecommendedFormatDefinition.xml into $EXPORTERDIR/targets/<your_log_exporter>/conf
* Navigate to the configuration file $EXPORTERDIR/targets/<your_log_exporter>/conf/targetConfigurationSample.xml and open it in edit mode.
* Add the reference to the SplunkRecommendedFormatDefinition.xml under the key <formatHeaderFile>. For example, if $EXPORTERDIR=/opt/CPrt-R81/log_exporter, the absolute path will become:  

```xml
<formatHeaderFile>/opt/CPrt-R81/log_exporter/targets/<your_log_exporter>/conf/SplunkRecommendedFormatDefinition.xml</formatHeaderFile>
```

* Restart cp_log_exporter by executing the command cp_log_export restart name <your_log_exporter>

* Warning: Make sure if you migrating to different format, the earlier format is disabled or else it would lead to data duplication.

