# loggen

Loggen is a tool used to load test syslog implementations.

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514
## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Product Manual | <https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.26/administration-guide/96#loggen.1>   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| syslogng:loggen | By default, loggen uses the legacy BSD-syslog message format.<br>BSD example:<br>`loggen --inet --dgram --number 1 <ip> <port>`<br>RFC5424 example:<br>`loggen --inet --dgram -PF --number 1 <ip> <port>`<br>Refer to above manual link for more examples.             |

### Index Configuration

| key            | index          | notes          |
|----------------|----------------|----------------|
| syslogng_loggen | main          | none          |

