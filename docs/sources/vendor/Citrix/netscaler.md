# Netscaler ADC/SDX

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514
* For RFC 5424 format use dedicated port

## Links

| Ref            | Link                                                                                                |
|----------------|-----------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2770/>                                                           |
| Product Manual | <https://docs.netscaler.com/en-us/citrix-adc/current-release/system/audit-logging/configuring-audit-logging.html> |

## Sourcetypes

| sourcetype                 | notes |
|----------------------------|-------|
| citrix:netscaler:syslog    | None  |
| citrix:netscaler:appfw     | None  |
| citrix:netscaler:appfw:cef | None  |

## Sourcetype and Index Configuration

| key              | sourcetype                 | index | notes |
|------------------|----------------------------|-------|-------|
| citrix_netscaler | citrix:netscaler:syslog    | netfw | none  |
| citrix_netscaler | citrix:netscaler:appfw     | netfw | none  |
| citrix_netscaler | citrix:netscaler:appfw:cef | netfw | none  |

## Source Setup and Configuration

* Follow vendor configuration steps per Product Manual above.

## Options

| Variable                                         | default      | description                                                                                                                         |
|--------------------------------------------------|--------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `SC4S_IGNORE_MMDD_LEGACY_CITRIX_NETSCALER`       | empty string | (empty/yes) Set to "yes" for parsing the date in format `dd/mm/yyyy` instead of `mm/dd/yyyy`.                                       |
| `SC4S_LISTEN_CITRIX_NETSCALER_RFC5424_TCP_PORT`  | empty string | Set the TCP port to listen for Citrix Netscaler RFC5424 syslog traffic.                                                             |
| `SC4S_LISTEN_CITRIX_NETSCALER_RFC5424_UDP_PORT`  | empty string | Set the UDP port to listen for Citrix Netscaler RFC5424 syslog traffic.                                                             |
| `SC4S_LISTEN_CITRIX_NETSCALER_RFC5424_TLS_PORT`  | empty string | Set the TLS port to listen for Citrix Netscaler RFC5424 syslog traffic.                                                             |
| `SC4S_LISTEN_CITRIX_NETSCALER_RFC5424_RFC5425_PORT` | empty string | Set the port to listen for Citrix Netscaler RFC5424 (RFC5425) traffic.                                                              |
