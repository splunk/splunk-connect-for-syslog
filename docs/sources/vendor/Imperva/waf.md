
# On-Premises WAF (SecureSphere WAF)

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | <https://splunkbase.splunk.com/app/2874/>                                                                 |
| Product Manual | <https://community.microfocus.com/dcvta86296/attachments/dcvta86296/partner-documentation-h-o/22/2/Imperva_SecureSphere_11_5_CEF_Config_Guide_2018.pdf> |

## Sourcetypes

| sourcetype               | notes |
|--------------------------|-------|
| imperva:waf              | none  |
| imperva:waf:firewall:cef | none  |
| imperva:waf:security:cef | none  |

### Index Configuration

| key                        | index    | notes          |
|----------------------------|----------|----------------|
| Imperva Inc._SecureSphere  | netwaf   | none           |

