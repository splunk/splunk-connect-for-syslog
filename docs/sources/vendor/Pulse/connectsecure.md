#  Pulse

## Key facts

* Requires vendor product by source configuration
* IETF Frames use port 601/tcp or 5425/TLS

## Links 

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | <https://splunkbase.splunk.com/app/3852/>                                 |
| JunOS TechLibrary | <https://help.ivanti.com/ps/legacy/PCS/9.1Rx/9.1R11/ps-pcs-sa-9.1r11.5-admin-guide.pdf> |

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

