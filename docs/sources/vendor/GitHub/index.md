# Enterprise Server

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  |                                                                 |
| Product Manual |  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| github:enterprise:audit     |  The audit logs of GitHub Enterprise server have information about audites actions performed by github user.  |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| github_ent    | github:enterprise:audit    | gitops         | None     |

