# Suricata

## Key facts
* Message format: Based on the default `eve-log.identity` value in `suricata.yaml`, which is "suricata"
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  |                                                                                                         |
| Product Manual | [Suricata Documentation](https://docs.suricata.io/)   |


## Sourcetypes

| sourcetype             | notes                                                                                                   |
|------------------------|---------------------------------------------------------------------------------------------------------|
| suricata:flow          | None                                                                                                    |
| suricata:dns           | None                                                                                                    |
| suricata:fileinfo      | None                                                                                                    |
| suricata:http          | None                                                                                                    |
| suricata:tls           | None                                                                                                    |
| suricata:stats         | None                                                                                                    |
| suricata:<event_type\>  | unlisted or new event_type (parsed but not guaranteed tested)                                           |

## Sourcetype and Index Configuration

| key                    | sourcetype            | index          | notes          |
|------------------------|-----------------------|----------------|----------------|
| suricata_suricata      | suricata:<event_type\> | netids         | none           |

## Options

| variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_SURICATA_SIMPLE_SOURCETYPE | false   | Set to 'yes' to assign a simple sourcetype 'suricata' to all events. Keep the default to assign compound sourcetypes such as 'suricata:flow', 'suricata:dns', etc. |