#  etp

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Technology Add-On for FireEye | <https://splunkbase.splunk.com/app/1904/>                                                          |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| fe_etp | source does not provide host name constant "etp.fireeye.com" is use regardless of region |

### Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| FireEye_ETP | fe_etp | fireeye |
