# Email Security Appliance (ESA)

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/1761/>                                                                |
| Product Manual | <https://www.cisco.com/c/en/us/td/docs/security/esa/esa14-0/user_guide/b_ESA_Admin_Guide_14-0.pdf> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cisco:esa:http     |  The HTTP logs of Cisco IronPort ESA record information about the secure HTTP services enabled on the interface.  |
| cisco:esa:textmail     |  Text mail logs of Cisco IronPort ESA record email information and status.  |
| cisco:esa:amp     |  Advanced Malware Protection (AMP) of Cisco IronPort ESA records malware detection and blocking, continuous analysis, and retrospective alerting details.   |
| cisco:esa:authentication     |  These logs record successful user logins and unsuccessful login attempts.   |
| cisco:esa:cef     |  The Consolidated Event Logs summarizes each message event in a single log line.  |
| cisco:esa:error_logs     |  Error logs of Cisco IronPort ESA records error that occured for ESA configurations or internal issues.   |
| cisco:esa:content_scanner     |  Content scanner logs of Cisco IronPort ESA scans messages that contain password-protected attachments for
malicious activity and data privacy. |
| cisco:esa:antispam     |  Anti-spam logs record the status of the anti-spam scanning feature of your system, including the status on receiving updates of the latest anti-spam rules. Also, any logs related to the Context Adaptive Scanning Engine are logged here.  |
| cisco:esa:system_logs     |  System logs record the boot information, virtual appliance license expiration alerts, DNS status information, and comments users typed using commit command.  |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| cisco_esa    | cisco:esa:http    | email          | None     |
| cisco_esa    | cisco:esa:textmail    | email          | None     |
| cisco_esa    | cisco:esa:amp    | email          | None     |
| cisco_esa    | cisco:esa:authentication    | email          | None     |
| cisco_esa    | cisco:esa:cef    | email          | None     |
| cisco_esa    | cisco:esa:error_logs    | email          | None     |
| cisco_esa    | cisco:esa:content_scanner    | email          | None     |
| cisco_esa    | cisco:esa:antispam    | email          | None     |
| cisco_esa    | cisco:esa:system_logs    | email          | None     |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-cisco_esa.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-cisco_esa[sc4s-vps] {
 filter { 
        host("^esa-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('cisco')
            product('esa')
        ); 
    };   
};

```
