# Vendor - Dell - VMware

## Product - Carbon Black Protection

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on CEF | none                                                  |
| Splunk Add-on Source Specific | https://bitbucket.org/SPLServices/ta-cef-imperva-incapsula/downloads/                                                               |


### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| cef        | Common sourcetype                                                                                                 |

### Source

| source     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| carbonblack:protection:cef       | Note this method of onboarding is not recommended for a more complete experience utilize the json format supported by he product with hec or s3                                                                            |

### Index Configuration

| key            | source     | index          | notes          |
|----------------|----------------|----------------|----------------|
| Carbon Black_Protection      | carbonblack:protection:cef      | epintel          | none          |

### Filter type

MSG Parse: This filter parses message content

### Options

Note listed for reference processing utilizes the Microsoft ArcSight log path as this format is a subtype of CEF

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_CEF_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_CEF_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_CEF | no | Enable archive to disk for this specific source |
| SC4S_DEST_CEF_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source |

* NOTE:  Set only _one_ set of CEF variables for the entire SC4S deployment, regardless of how
many ports are in use by this CEF source (or any others).  See the "Common Event Format" source
documentation for more information.

### Verification

An active site will generate frequent events use the following search to check for new events

Verify timestamp, and host values match as expected

```
index=<asconfigured> (sourcetype=cef source="carbonblack:protection:cef")
```


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
| vmware:vsphere:vcenter | None |
| nix:syslog | When used with a default port, this will follow the generic NIX configuration. When using a dedicated port, IP or host rules events will follow the index configuration for vmware nsx  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| vmware_vsphere_esx      | vmware:vsphere:esx | main          | none          |
| vmware_vsphere_nsx      | vmware:vsphere:nsx | main          | none          |
| vmware_vsphere_vcenter      | vmware:vsphere:vcenter | main          | none          |

### Filter type

MSG Parse: This filter parses message content when using the default configuration

### Setup and Configuration

* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_VMWARE_VSPHERE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_VMWARE_VSPHERE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_VMWARE_VSPHERE_TLS_PORT      | empty string      | Enable a TLS port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_VMWARE_VSPHERE | no | Enable archive to disk for this specific source |
| SC4S_DEST_VMWARE_VSPHERE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype="vmware:vsphere:*" | stats count by host
```

# Vendor - Dell - VMware

## Product - Horizon View 


| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Manual | unknown |

### Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| vmware:horizon | None |
| nix:syslog | When used with a default port this will follow the generic NIX configuration when using a dedicated port, IP or host rules events will follow the index configuration for vmware nsx  |

### Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| vmware_horizon      | vmware:horizon | main          | none          |

### Filter type

MSG Parse: This filter parses message content when using the default configuration

### Setup and Configuration

* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
    * Select TCP or SSL transport option
    * Ensure the format of the event is customized per Splunk documentation

### Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_VMWARE_VSPHERE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_VMWARE_VSPHERE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_VMWARE_VSPHERE_TLS_PORT      | empty string      | Enable a TLS port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_VMWARE_VSPHERE | no | Enable archive to disk for this specific source |
| SC4S_DEST_VMWARE_VSPHERE_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Verification

An active device will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype="vmware:horizon" | stats count by host
```
