# Log Exporter (Syslog)

## Key Facts

- As of 2/1/2022, the Log Exporter configuration provided by Checkpoint is defective and produces invalid data. The configuration below is **REQUIRED**.
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

### Splunk Side

- Install the Splunk Add-on on the search head(s) for the users interested in this data source. If SC4S is used exclusively, the add-on is not required on the target indexer or heavy forwarder.
- Review and update the `splunk_metadata.csv` file and set the `index` and `sourcetype` as required for the data source.

### Checkpoint Side

1. Go to the `cp` terminal and use the `expert` command to log-in in expert mode.
2. Ensure the built-in variable `$EXPORTERDIR` shell variable is defined with:

```sh
echo "$EXPORTERDIR"
```

2. Create a new Log Exporter target in `$EXPORTERDIR/targets` with:

```sh
LOG_EXPORTER_NAME='SyslogToSplunk' # Name this something unique but meaningful
TARGET_SERVER='example.internal' # The indexer or heavy forwarder to send logs to. Can be an FQDN or an IP address.
TARGET_PORT='514' # Syslog defaults to 514
TARGET_PROTOCOL='tcp' # IETF Syslog is specifically TCP

cp_log_export add name "$LOG_EXPORTER_NAME" target-server "$TARGET_SERVER" target-port "$TARGET_PORT" protocol "$TARGET_PROTOCOL" format 'syslog'
```

3. Make a global copy of the built-in Syslog format definition with:

```sh
cp "$EXPORTERDIR/conf/SyslogFormatDefinition.xml" "$EXPORTERDIR/conf/SplunkRecommendedFormatDefinition.xml"
```

4. Edit `$EXPORTERDIR/conf/SplunkRecommendedFormatDefinition.xml` by modifying the `start_message_body`, `fields_separatator`, and `field_value_separatator` keys as shown below.
   a. **Note**: The misspelling of "separator" as "separatator" is _intentional_, and is to line up with both Checkpoint's documentation and parser implementation.

```xml
<start_message_body>[sc4s@2620 </start_message_body>
<!-- ... -->
<fields_separatator> </fields_separatator>
<!-- ... -->
<field_value_separatator>=</field_value_separatator>
```

6. Copy the new format config to your new target's `conf` directory with:

```sh
cp "$EXPORTERDIR/conf/SplunkRecommendedFormatDefinition.xml"  "$EXPORTERDIR/targets/$LOG_EXPORTER_NAME/conf"

```

7. Edit `$EXPORTERDIR/targets/$LOG_EXPORTER_NAME/targetConfiguration.xml` by adding the reference to the `$EXPORTERDIR/targets/$LOG_EXPORTER_NAME/conf/SplunkRecommendedFormatDefinition.xml` under the key `<formatHeaderFile>`.
   a. For example, if `$EXPORTERDIR` is `/opt/CPrt-R81/log_exporter` and `$LOG_EXPORTER_NAME` is `SyslogToSplunk`, the absolute path will become:

```xml
<formatHeaderFile>/opt/CPrt-R81/log_exporter/targets/SyslogToSplunk/conf/SplunkRecommendedFormatDefinition.xml</formatHeaderFile>
```

8. Restart the new log exporter with:

```sh
cp_log_export restart name "$LOG_EXPORTER_NAME"
```

9. **Warning**: If you're migrating from the old Splunk Syslog format, make sure that the older format's log exporter is disabled, as it would lead to data duplication.
