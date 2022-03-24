# Merged Audit

XY Pro merged audit also called XYGate or XMA is the defacto solution for syslog from HP Nonstop Server (Tandem)

## Key facts

* Legacy BSD Format default port 514 CEF Format

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                  |
| Product Manual | <https://xypro.com/products/hpe-software-from-xypro/>   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | None                                                                                                    |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| XYPRO_NONSTOP      | cef       | infraops          | none          |
