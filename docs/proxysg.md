This add-on allows a Splunk software administrator to collect bluecoat weblog data from Blue Coat ProxySG log files in **W3C ELFF format.** 

#### Versions Supported

Symantec ProxySG 6.X

#### Configuring Bluecoat for Syslog

From IBM:
https://www.ibm.com/support/knowledgecenter/en/SS42VS_DSM/com.ibm.dsm.doc/t_DSM_guide_BlueCoat_cfg_syslog.html?cp=SS42VS_7.3.2

***Note in step 6 above use the IP address of your Syslog-ng server**

From Symantec:
https://support.symantec.com/us/en/article.tech241702.html

#### Installing Splunk TA for ProxySG

Splunk TA Download: https://splunkbase.splunk.com/app/2758/
More Information: https://docs.splunk.com/Documentation/AddOns/latest/BlueCoatProxySG/About

**It is assumed you have the default log formats as well as default header formats in your syslog server running on port 514(UDP).**
