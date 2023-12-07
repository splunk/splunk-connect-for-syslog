# EPO

## Key facts

* MSG Format based filter
* Source requires use of TLS legacy BSD port 6514
* TLS Certificate must be trusted by EPO instance

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/5085/>                                                   |
| Product Manual | <https://kc.mcafee.com/corporate/index?page=content&id=KB87927> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| mcafee:epo:syslog | none |

## Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| policy_auditor_vulnerability_assessment        | Policy Auditor Vulnerability Assessment events |
| mcafee_agent                                   | McAfee Agent events |
| mcafee_endpoint_security                       | McAfee Endpoint Security events |

### Index Configuration

| key            | index      | notes          |
|----------------|------------|----------------|
| mcafee_epo     | epav          | none          |

### Filter type

MSG Parse: This filter parses message content

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_MCAFEE_EPO_TLS_PORT      | empty string      | Enable a TLS port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_DEST_MCAFEE_EPO_ARCHIVE | no | Enable archive to disk for this specific source |
| SC4S_DEST_MCAFEE_EPO_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |
| SC4S_SOURCE_TLS_ENABLE | no | This must be set to yes so that SC4S listens for encrypted syslog from ePO

### Additional setup

You must create a certificate for the SC4S server to receive encrypted syslog from ePO. A self-signed certificate is fine. Generate a self-signed certificate on the SC4S host:

`openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout /opt/sc4s/tls/server.key -out /opt/sc4s/tls/server.pem`

Uncomment the following line in `/lib/systemd/system/sc4s.service` to allow the docker container to use the certificate:

`Environment="SC4S_TLS_DIR=-v   :/etc/syslog-ng/tls:z"`

### Troubleshooting

from the command line of the SC4S host, run this: `openssl s_client -connect localhost:6514`

The message:

```
socket: Bad file descriptor
connect:errno=9
```

indicates that SC4S is not listening for encrypted syslog. Note that a `netstat` may show the port open, but it is not accepting encrypted traffic as configured.

It may take several minutes for the syslog option to be available in the `registered servers` dropdown.
