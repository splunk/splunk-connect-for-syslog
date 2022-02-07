# Ossec

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2808/>                                                                |
| Product Manual | <https://www.ossec.net/docs/index.html> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| ossec     |  The add-on supports data from the following sources: File Integrity Management (FIM) data, FTP data, su data, ssh data, Windows data, including audit and logon information  |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| ossec_ossec    | ossec    | main          | None     |
