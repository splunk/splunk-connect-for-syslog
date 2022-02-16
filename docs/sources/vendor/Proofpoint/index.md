# Proofpoint Protection Server

## Key facts

* Requires vendor product by source configuration
* Legacy BSD Format default port 514
* NOTE:  This filter will simply parse the syslog message itself, and will _not_ perform the (required) re-assembly of related
messages to create meaningful final output.  This will require follow-on processing in Splunk.

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/3080/>                                                                 |
| Product Manual | <https://proofpointcommunities.force.com/community/s/article/Remote-Syslog-Forwarding>                    |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| pps_filter_log |                                                                               |
|  pps_mail_log  | This sourcetype will conflict with sendmail itself, so will require that the PPS send syslog on a dedicated port or be uniquely identifiable with a hostname glob or CIDR block if this sourcetype is desired for PPS.   |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| proofpoint_pps_filter        | pps_filter_log       | email          | none          |
| proofpoint_pps_sendmail      | pps_mail_log       | email          | none          |

## Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-proofpoint_pps.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-proofpoint_pps[sc4s-vps] {
 filter { 
        host("pps-*" type(glob))
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('proofpoint')
            product('pps')
        ); 
    };   
};


```
