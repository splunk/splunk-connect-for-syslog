# Array

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None  note TA published on Splunk base does not include syslog extractions                                                                |
| Product Manual |  |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| purestorage:array     |   |
| purestorage:array:${class} | This type is generated from the message |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| purestorage_array    | purestorage:array    | infraops          | None     |
| purestorage_array_${class}    | purestorage:array:class    | infraops          | class is extracted as the string following "purity."     |

