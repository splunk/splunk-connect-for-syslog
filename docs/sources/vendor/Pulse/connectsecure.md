#  Pulse

## Key facts

* Requires vendor product by source configuration
* IETF Frames use port 601/tcp or 5425/TLS

## Links 

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | <https://splunkbase.splunk.com/app/3852/>                                 |
| JunOS TechLibrary | <https://docs.pulsesecure.net/WebHelp/Content/PCS/PCS_AdminGuide_8.2/Configuring%20Syslog.htm> |

## Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| pulse:connectsecure  | None                                                             |
| pulse:connectsecure:web   | None                                                             |

## Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| pulse_connect_secure         | pulse:connectsecure | netfw          | none          |
| pulse_connect_secure_web          | pulse:connectsecure:web      | netproxy         | none          |

