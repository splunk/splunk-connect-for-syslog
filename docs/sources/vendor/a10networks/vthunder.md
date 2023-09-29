# a10networks vthunder

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref                                   | Link                                                                             |
|---------------------------------------|----------------------------------------------------------------------------------|
| A10 Networks SSL Insight App          | <https://splunkbase.splunk.com/app/3937>                                         |
| A10 Networks Application Firewall App | <https://splunkbase.splunk.com/app/3920>                                         |
| A10 Networks L4 Firewall App          | <https://splunkbase.splunk.com/app/3910>                                         |


## Sourcetypes

| sourcetype                  | notes                                                                                      |
|-----------------------------|--------------------------------------------------------------------------------------------|
| a10networks:vThunder:cef    | CEF                                                                                        |
| a10networks:vThunder:syslog | Syslog                                                                                     |

## Source

| source               | notes                                                                                             |
|----------------------|---------------------------------------------------------------------------------------------------|
| a10networks:vThunder | None                                                                                              |

### Index Configuration

| key                | source              | index                  | notes          |
|--------------------|---------------------|------------------------|----------------|
|a10networks_vThunder| a10networks:vThunder| netwaf, netops         | none           |
