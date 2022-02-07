# MFP

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ricoh:mfp        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ricoh_syslog      | ricoh:mfp       | printer          | none          |

## SC4S Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_SOURCE_RICOH_SYSLOG_FIXHOST | yes | Current firmware incorrectly sends the value of HOST in the program field if this is ever corrected this value will need to be set back to no we suggest using yes |

