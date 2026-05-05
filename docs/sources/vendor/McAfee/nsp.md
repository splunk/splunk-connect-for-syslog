
# Network Security Platform

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Product Manual | <https://docs-be.trellix.com/bundle/network-security-platform-v8-3-0-quick-tour-product/raw/resource/enus/PD26342.pdf> |

## Sourcetypes

| sourcetype | notes |
| ---------- | ----- |
| mcafee:nsp | none  |

## Source

| source              | notes                               |
| ------------------- | ----------------------------------- |
| mcafee:nsp:alert    | Alert/Attack Events                 |
| mcafee:nsp:audit    | Audit Event or User Activity Events |
| mcafee:nsp:fault    | Fault Events                        |
| mcafee:nsp:firewall | Firewall Events                     |

### Index Configuration

| key        | index      | notes |
| ---------- | ---------- | ----- |
| mcafee_nsp | netids     | none  |

