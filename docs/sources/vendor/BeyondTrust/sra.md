# Secure Remote Access (Bomgar)

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
| beyondtrust:sra        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| beyondtrust_sra     | beyondtrust:sra       | infraops          | none          |

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_DEST_BEYONDTRUST_SRA_SPLUNK_HEC_FMT | JSON | Restructure data from vendor format to json for splunk destinations set to "NONE" for native format |
| SC4S_DEST_BEYONDTRUST_SRA_SYSLOG_FMT | SDATA | Restructure data from vendor format to SDATA for SYSLOG destinations set to "NONE" for native ormat|
