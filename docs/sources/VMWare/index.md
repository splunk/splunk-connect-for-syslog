# Vendor - Dell - VMware

## Product - vSphere - ESX NSX (Controller, Manager, Edge)


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Manual | https://docs.vmware.com/en/VMware-NSX-Data-Center-for-vSphere/6.4/com.vmware.nsx.logging.doc/GUID-0674A29A-9D61-4E36-A302-E4192A3DA1A5.html |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| vmware:vsphere:nsx | None |
| vmware:vsphere:esx | None |
| nix:syslog | When used with a default port this will follow the generic NIX configuration when using a dedicated port, IP or host rules events will follow the index configuration for vmware nsx  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| vmware_nsx      | vmware:vsphere:nsx | main          | none          |
| vmware_esx      | vmware:vsphere:esx | main          | none          |

### Filter type

MSG Parse: This filter parses message content when using the default configuration

### Setup and Configuration

* Review and update the splunk_index.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_VMWARE_VSPHERE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using the number defined |
| SC4S_LISTEN_VMWARE_VSPHERE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using the number defined |
| SC4S_LISTEN_VMWARE_VSPHERE_TLS_PORT      | empty string      | Enable a TLS port for this specific vendor product using the number defined |
| SC4S_ARCHIVE_VMWARE_VSPHERE | no | Enable archive to disk for this specific source |
| SC4S_DEST_VMWARE_VSPHERE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype="vmware:*:vsphere:*" | stats count by host
```
