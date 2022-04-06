# Digital Network Area(DNA)

## Key facts

* MSG Format based filter
* rfc5424 default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | na                                                               |
| Product Manual | multiple |

## Sourcetypes

| sourcetype | notes                                                                                                   |
|------------|---------------------------------------------------------------------------------------------------------|
| cisco:dna  |  None                                                                                                    |

## Sourcetype and Index Configuration

| key       | sourcetype | index  | notes          |
|-----------|------------|--------|----------------|
| cisco_dna | cisco:dna  | netops | None     |

## SC4S Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_SOURCE_CISCO_DNA_FIXHOST | yes | Current firmware incorrectly sends the value of the syslog server host name (destination) in the host field if this is ever corrected this value will need to be set back to no we suggest using yes |
