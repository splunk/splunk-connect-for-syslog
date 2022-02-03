# Vendor - Beyond Trust


## Product - Secure Remote Access (Bomgar)

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| beyondtrust:sra        | None                                                                                                    |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| beyondtrust_sra     | beyondtrust:sra       | infraops          | none          |

### Filter type

MSG Parsing

### Setup and Configuration

Device setup unknown 

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_ARCHIVE_BEYONDTRUST_SRA | no | Enable archive to disk for this specific source |
| SC4S_DEST_BEYONDTRUST_SRA_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 
| SC4S_DEST_BEYONDTRUST_SRA_SPLUNK_HEC_FMT | json | Restructure data from vendor format to json for splunk destinations |
| SC4S_DEST_BEYONDTRUST_SRA_SYSLOG_FMT | json | Restructure data from vendor format to SDATA for SYSLOG destinations |

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype=beyondtrust:sra | stats count by host
```
