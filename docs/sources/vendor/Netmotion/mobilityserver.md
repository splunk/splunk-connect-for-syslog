# Mobility Server

## Key facts

* MSG Format based filter


## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | none                                                  |
| Product Manual | unknown |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| netmotion:mobilityserver:*  | The third segment of the source type is constructed from the sdid field of the syslog sdata |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| netmotion_mobility-server_*      | netmotion:mobilityserver:*    | netops          | none          |

