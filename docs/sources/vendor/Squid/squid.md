# Squid Web Proxy

## Key facts
* Filtered based on the message when [splunk_recommended_squid](https://docs.splunk.com/Documentation/AddOns/released/Squid/Setup) format has been configured
* Else requires vendor product by source configuration

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/2965                                                                |
| Splunk Add-on | https://docs.splunk.com/Documentation/AddOns/released/Squid/About |
| Product Manual | [Customizable Log Formats](https://wiki.squid-cache.org/Features/LogFormat)  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| squid:access:recommended        | requires the [splunk_recommended_squid](https://docs.splunk.com/Documentation/AddOns/released/Squid/Setup) format                                                                                               |
| squid:access        | default Squid format                                                                                          |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| squid_access      | squid:access:recommended, squid:access       | netproxy          | none          |
