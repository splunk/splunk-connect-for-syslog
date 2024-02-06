# Log Exporter (Syslog)

## Key Facts

- As of 2/1/2022, the Log Exporter configuration provided by CheckPoint is defective and produces invalid data. The configuration below is _REQUIRED_.
- MSG format-based filter
- RFC5424 IETF Syslog without frame -- use port `514/TCP`.

| Ref            | Link                                                                    |
| -------------- | ----------------------------------------------------------------------- |
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4293>                                |
| Product Manual | <https://sc1.checkpoint.com/documents/App_for_Splunk/html_frameset.htm> |

## Sourcetypes

| sourcetype    | notes |
| ------------- | ----- |
| cp_log:syslog | None  |

## Sourcetype and Index Configuration

| key               | sourcetype    | index  | notes |
| ----------------- | ------------- | ------ | ----- |
| checkpoint_syslog | cp_log:syslog | netops | none  |

## Source and Index Configuration

Checkpoint Software blades with a CIM mapping have been sub-grouped into sources
to allow routing to appropriate indexes. All other source metadata is left as their defaults.

| key                           | source      | index    | notes |
| ----------------------------- | ----------- | -------- | ----- |
| checkpoint_syslog_dlp         | dlp         | netdlp   | none  |
| checkpoint_syslog_email       | email       | email    | none  |
| checkpoint_syslog_firewall    | firewall    | netfw    | none  |
| checkpoint_syslog_sessions    | sessions    | netops   | none  |
| checkpoint_syslog_web         | web         | netproxy | none  |
| checkpoint_syslog_audit       | audit       | netops   | none  |
| checkpoint_syslog_endpoint    | endpoint    | netops   | none  |
| checkpoint_syslog_network     | network     | netops   |       |
| checkpoint_syslog_ids         | ids         | netids   |       |
| checkpoint_syslog_ids_malware | ids_malware | netids   |       |

## Source Configuration

- Install the Splunk Add-on on the search head(s) for the users interested in this data source. If SC4S is used exclusively, the add-on is not required on the indexer.
- Review and update the `splunk_metadata.csv` file and set the `index` and `sourcetype` as required for the data source.
- To configure the valid Syslog format in Checkpoint, follow the steps below:
- Go to the `cp` terminal.
- Enter `expert` command for login in expert mode.
- Enter `cd $EXPORTERDIR`.
- In this directory check targets if it's empty then configure a new target for the logs with help of below command:

```sh
cp_log_export add name $YOUR_LOG_EXPORTER target-server $TARGET_SERVER_IP_ADDRESS target-port $TARGET_PORT protocol $UDP_OR_TCP format $SYSLOG_OR_CEF_OR_SPLUNK_GENERIC
```

- Navigate to the `conf/` directory.
- Enter `cp SyslogFormatDefinition.xml SplunkRecommendedFormatDefinition.xml`.
- Open `SplunkRecommendedFormatDefinition.xml` in edit mode and modify the `start_message_body`, `fields_separator`, and `field_value_separator` keys as shown below.

```xml
<start_message_body>[sc4s@2620 </start_message_body>
```

```xml
<fields_separator> </fields_separator>
```

```xml
<field_value_separator>=</field_value_separator>
```

- Copy `SplunkRecommendedFormatDefinition.xml` into `$EXPORTERDIR/targets/<your_log_exporter>/conf`.
- Navigate to the configuration file `$EXPORTERDIR/targets/<your_log_exporter>/targetConfiguration.xml` and open it in edit mode.
- Add the reference to the `SplunkRecommendedFormatDefinition.xml` under the key `<formatHeaderFile>`. For example, if `$EXPORTERDIR=/opt/CPrt-R81/log_exporter`, the absolute path will become:

```xml
<formatHeaderFile>/opt/CPrt-R81/log_exporter/targets/<your_log_exporter>/conf/SplunkRecommendedFormatDefinition.xml</formatHeaderFile>
```

- Restart `cp_log_exporter` by running the command `cp_log_export restart name <your_log_exporter>`.

- _Warning_: Make sure if you're migrating from the old Splunk Syslog format that the older format is disabled, as it would lead to data duplication.
