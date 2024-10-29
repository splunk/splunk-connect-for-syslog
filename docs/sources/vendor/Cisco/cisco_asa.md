# ASA/FTD (Firepower)

## Key facts

* MSG Format based filter
* None conformant legacy BSD Format default port 514


# Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on for ASA (No long supports FWSM and PIX) | <https://splunkbase.splunk.com/app/1620/>                                                          |
| Product Manual | <https://www.cisco.com/c/en/us/support/docs/security/pix-500-series-security-appliances/63884-config-asa-00.html> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:asa      | cisco FTD Firepower will also use this source type except those noted below                                                      |
| cisco:ftd      | cisco FTD Firepower will also use this source type except those noted below                                                      |
| cisco:fwsm      | Splunk has   |
| cisco:pix      | cisco PIX will also use this source type except those noted below                                                      |
| cisco:firepower:syslog | FTD Unified events see <https://www.cisco.com/c/en/us/td/docs/security/firepower/Syslogs/b_fptd_syslog_guide.pdf> |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_asa      | cisco:asa      | netfw          | none           |
| cisco_fwsm      | cisco:fwsm      | netfw          | none           |
| cisco_pix      | cisco:pix      | netfw          | none           |
| cisco_firepower      | cisco:firepower:syslog      | netids          | none           |
| cisco_ftd      | cisco:ftd      | netfw          | none           |

## Source Setup and Configuration

* Follow vendor configuration steps per Product Manual above ensure:
  * Log Level is 6 "Informational"
  * Protocol is TCP/IP
  * permit-hostdown is on
  * device-id is hostname and included
  * timestamp is included

