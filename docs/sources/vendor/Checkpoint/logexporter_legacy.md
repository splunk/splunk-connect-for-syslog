# Log Exporter (Splunk)

The "Splunk Format" is legacy and should not be used for new deployments see Log Exporter (Syslog)

## Key Facts

* Format is not conformant to RFC3164 avoid use
* MSG Format based filter
* Legacy BSD Format default port 514

The Splunk `host` field will be derived as follows using the first match

* Use the hostname field
* Use the first CN component of origin_sic_name/originsicname
* If host is not set from CN use the `hostname` field
* If host is not set use the BSD syslog header host

If the host is in the format `<host>-v_<bladename>` use `bladename` for host

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/4293/>                                                                 |
| Product Manual | <https://sc1.checkpoint.com/documents/App_for_Splunk/html_frameset.htm> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cp_log         | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| checkpoint_splunk         | cp_log         | netops         | none           |

## Source and Index Configuration

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

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CHECKPOINT_SPLUNK_NOISE_CONTROL | no | Suppress any duplicate product+loguid pairs processed within 2 seconds of the last matching event |
| SC4S_LISTEN_CHECKPOINT_SPLUNK_OLD_HOST_RULES | empty string | when set to `yes` reverts host name selection order to originsicname-->origin_sic_name-->hostname |
