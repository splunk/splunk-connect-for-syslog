
# Network Security Platform

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Product Manual | <https://docs.mcafee.com/bundle/network-security-platform-10.1.x-product-guide/page/GUID-373C1CA6-EC0E-49E1-8858-749D1AA2716A.html> |

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

