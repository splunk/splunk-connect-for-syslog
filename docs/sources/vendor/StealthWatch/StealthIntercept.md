# Stealth Intercept

## Key facts

* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | https://splunkbase.splunk.com/app/4609/                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| StealthINTERCEPT        | None                                                                                                    |
| StealthINTERCEPT:alerts  | SC4S Format Shifts to JSON override template to `t_msg_hdr` for original raw |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| stealthbits_stealthintercept      | StealthINTERCEPT       | netids          | none          |
| stealthbits_stealthintercept_alerts      | StealthINTERCEPT:alerts       | netids          | Note TA does not support this source type          |

