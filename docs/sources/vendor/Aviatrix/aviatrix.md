# Switch

## Key facts
* MSG Format based filter
* Legacy BSD Format default port 514

## Product - Switches

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | --                                    |
| Product Manual | [Link](https://docs.aviatrix.com/documentation/latest/controller-platform-administration/aviatrix-logging.html?expand=true#log-management-system-formats)   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| aviatrix:cloudx-cli       | None                                                                                         |
| aviatrix:kernel      | None                                                                                         |
| aviatrix:cloudxd      | None                                                                                         |
| aviatrix:avx-nfq     | None                                                                                         |
| aviatrix:avx-gw-state-sync     | None                                                                                         |
| aviatrix:perfmon    | None                                                                                         |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| aviatrix_cloudx-cli | aviatrix:cloudx-cli       |          | none          |
| aviatrix_kernel     |   aviatrix:kernel         |          | none          |
| aviatrix_cloudxd    |  aviatrix:cloudxd         |          | none          |
| aviatrix_avx-nfq    |   aviatrix:avx-nfq        |          | none          |
| aviatrix_avx-gw-state-sync |   aviatrix:avx-gw-state-sync     |       | none          |
| aviatrix_perfmon    |   aviatrix:perfmon        |          | none          |
