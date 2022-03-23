
## Product - vSphere - ESX NSX (Controller, Manager, Edge)

Vmware vsphere product line has multiple old and known issues in syslog output.

* GUID values sent in place of time stamp
* Improper time stamp in all RFC5424 events
* No PRI
* No syslog header for some split events
* mismatch syslog header for some split events (segment 1 contains header remaining segments contain no header)

WARNING use of a load balancer with udp will cause "corrupt" event behavior due to out of order message processing caused by the load balancer

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                                                |
| Manual | <https://docs.vmware.com/en/VMware-NSX-Data-Center-for-vSphere/6.4/com.vmware.nsx.logging.doc/GUID-0674A29A-9D61-4E36-A302-E4192A3DA1A5.html> |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| `vmware:esxlog:${PROGRAM}` | None |
| `vmware:nsxlog:${PROGRAM}` | None |
| `vmware:vclog:${PROGRAM}` | None |
| nix:syslog | When used with a default port, this will follow the generic NIX configuration. When using a dedicated port, IP or host rules events will follow the index configuration for vmware nsx  |

## Sourcetype and Index Configuration

| key            | sourcetype     | index          | notes          |
|----------------|----------------|----------------|----------------|
| vmware_vsphere_esx      | `vmware:esxlog:${PROGRAM}` | infraops          | none          |
| vmware_vsphere_nsx      | `vmware:nxlog:${PROGRAM}` | infraops          | none          |
| vmware_vsphere_vcenter      | `vmware:vclog:${PROGRAM}` | infraops          | none          |

### Filter type

MSG Parse: This filter parses message content when using the default configuration.
SC4S will normalize the structure of vmware events from multiple incorrectly formed varients to rfc5424 format to improve parsing

## Setup and Configuration

* Review and update the splunk_metadata.csv file and set the index and sourcetype as required for the data source.
* Refer to the Splunk TA documentation for the specific customer format required for proxy configuration
  * Select TCP or SSL transport option
  * Ensure the format of the event is customized per Splunk documentation

## Options

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_VMWARE_VSPHERE_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_VMWARE_VSPHERE_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_VMWARE_VSPHERE_TLS_PORT      | empty string      | Enable a TLS port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_SOURCE_VMWARE_VSPHERE_GROUPMSG      | empty string      | empty/yes groups known instances of improperly split events set "yes" to return to enable  |

### Verification

An active proxy will generate frequent events. Use the following search to validate events are present per source device

```
index=<asconfigured> sourcetype="vmware:vsphere:*" | stats count by host
```

## Automatic Parser Configuration

Enable the following options in the env_file

```bash
#Do not enable with a SNAT load balancer
SC4S_USE_NAME_CACHE=yes
#Combine known split events into a single event for Splunk
SC4S_SOURCE_VMWARE_VSPHERE_GROUPMSG=yes
#Learn vendor product from recognized events and apply to generic events
#for example after the first vpxd event sshd will utilize vps "vmware_vsphere_nix_syslog" rather than "nix_syslog"
SC4S_USE_VPS_CACHE=yes
```

## Manual Parser Configuration

```c
#/opt/sc4s/local/config/app-parsers/app-vps-vmware_vsphere.conf
#File name provided is a suggestion it must be globally unique

application app-vps-test-vmware_vsphere[sc4s-vps] {
 filter {      
        #netmask(169.254.100.1/24)
        #host("-esx-")
    }; 
    parser { 
        p_set_netsource_fields(
            vendor('vmware')
            product('vsphere')
        ); 
    };   
};

```
