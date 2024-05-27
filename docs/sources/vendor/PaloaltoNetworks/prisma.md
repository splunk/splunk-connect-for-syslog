# Prisma SD-WAN ION

## Key facts
* MSG Format based filter

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                                                 |
| Product Manual | https://docs.paloaltonetworks.com/prisma/prisma-sd-wan/prisma-sd-wan-admin/prisma-sd-wan-sites-and-devices/use-external-services-for-monitoring/syslog-server-support-in-prisma-sd-wan                                                                 |
| Product Manual | https://docs.paloaltonetworks.com/prisma/prisma-sd-wan/prisma-sd-wan-admin/prisma-sd-wan-sites-and-devices/use-external-services-for-monitoring/syslog-server-support-in-prisma-sd-wan/syslog-flow-export |

## Sourcetypes

| sourcetype               | notes |
|--------------------------|-------|
| prisma:sd-wan:flow | | none |
| prisma:sd-wan:authentication | | none |
| prisma:sd-wan:event | | none |

### Index Configuration

| key                        | index    | notes          |
|----------------------------|----------|----------------|
| prisma_sd-wan_flow  | netwaf   | none           |
| prisma_sd-wan_authentication  | netwaf   | none           |
| prisma_sd-wan_event  | netwaf   | none           |

