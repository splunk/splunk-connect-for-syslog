# Enterprise Security CEF

The TA link provided has commented out the CEF support as of 2022-03-18
manual edits are required

## Key facts

* MSG Format based filter
* RFC5424

## Links

| Ref               | Link                                                                    |
|-------------------|-------------------------------------------------------------------------|
| Splunk Add-on     | https://splunkbase.splunk.com/app/4656/                               |


## Sourcetypes

| sourcetype               | notes                                                            |
|--------------------------|------------------------------------------------------------------|
| kaspersky:cef   |                                                            |
| kaspersky:klaud |
| kaspersky:klsrv   |                                                              |
| kaspersky:gnrl   |                                                              |
| kaspersky:klnag   |                                                              |
| kaspersky:klprci   |                                                              |
| kaspersky:klbl   |                                                              |

## Sourcetype and Index Configuration

| key                        | sourcetype             | index          | notes         |
|----------------------------|------------------------|----------------|---------------|
| KasperskyLab_SecurityCenter         | all | epav          | none          |
