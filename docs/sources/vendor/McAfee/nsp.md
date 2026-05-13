
# Network Security Platform

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Product Manual | <https://docs.trellix.com/nl-NL/bundle/virtual-network-security-platform-v9-1-7-v9-1-7-15-v9-1-7-4-release-notes/resource/PD27368.pdf> |

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

