## Palo Alto Syslog Connector for Splunk Palo Alto TA

#### **Versions Supported**

This filter works for anything running PAN-OS so every product in the Palo Alto Networks Next-generation Security Platform will be compatible with this filter. See the Splunk compatibility guide for complete version details: https://splunk.paloaltonetworks.com/compatibility.html 

#### Adding Palo Alto Networks Add-on and App to Splunk

###### **Palo Alto Networks Add-on for Splunk:**

Download: https://splunkbase.splunk.com/app/2757/

Installation Guide: https://splunk.paloaltonetworks.com/installation.html

Syslog Specific Field Descriptions: https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-admin/monitoring/use-syslog-for-monitoring/syslog-field-descriptions.html

###### **Setting up Syslog within PAN-OS:**

Splunk handles the following log types: **traffic, threat, system, configuration, hipwatch, correlation, userid.** The other log types are _**not**_ guaranteed to get parsed correctly. Also make sure to **use BSD format for the syslog server setup**, as it is assumed you have the default log formats as well as default header formats in your syslog server listening on port 514(UDP). (See Steps 1 and 4 in the documentation linked below)  

###### Configuring PAN OS Device for use with syslog

PAN OS Version 9.0 
https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-admin/monitoring/use-syslog-for-monitoring/configure-syslog-monitoring.html

PAN OS Version 8.1 
https://docs.paloaltonetworks.com/pan-os/8-1/pan-os-admin/monitoring/use-syslog-for-monitoring/configure-syslog-monitoring

PAN OS Version 8.0
https://docs.paloaltonetworks.com/pan-os/8-0/pan-os-admin/monitoring/use-syslog-for-monitoring/configure-syslog-monitoring

PAN OS Version 7.1
https://docs.paloaltonetworks.com/pan-os/7-1/pan-os-admin/monitoring/configure-syslog-monitoring

More detailed guide: https://knowledgebase.paloaltonetworks.com/KCSArticleDetail?id=kA10g000000ClRxCAK

**List of Palo Alto Log Types:** 

PAN OS Version 9.0
https://docs.paloaltonetworks.com/pan-os/9-0/pan-os-web-interface-help/monitor/monitor-logs/log-types.html

PAN OS Version 8.1
https://docs.paloaltonetworks.com/pan-os/8-1/pan-os-web-interface-help/monitor/monitor-logs/log-types.html

PAN OS Version 8.0
https://docs.paloaltonetworks.com/pan-os/8-0/pan-os-web-interface-help/monitor/monitor-logs/log-types.html
