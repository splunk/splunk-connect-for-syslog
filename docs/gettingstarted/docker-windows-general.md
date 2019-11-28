
# Install Docker on Windows Server

This guide was developed on a Windows Server DataCenter 2019 build 1903 
using nested hyper-v (Azure D2S_V3) this configuration is described as 
experimental by both Mircosoft and Docker. the SC4S Project recommends 
using one of the Linux variants for production use until the LCOW (Docker Windows)
feature transitions to release/stable. However if no other option is possible
and the appropriate internal stakeholders accept the risk go forth.

Performance testing should be conducted using the specific production 
configuration as this is not being done by the SC4S project at this time.


# Setup

* Install and enable hyper-v, a restart may be required between steps below

```powershell
# Enable Hyper-v note this requires restart
Install-WindowsFeature rsat-hyper-v-tools -All
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
Get-VM WinContainerHost | Set-VMProcessor -ExposeVirtualizationExtensions $true
```

* Install and enable docker

```powershell
Install-Module DockerProvider
Install-Package Docker -ProviderName DockerProvider -RequiredVersion preview
[Environment]::SetEnvironmentVariable("LCOW_SUPPORTED", "1", "Machine")
```

* Verify Docker a bash prompt should be presented exit by typing ```exit```

```powershell
#verify docker is working with a linux vm type exit to end the bash session
docker run -it --rm ubuntu /bin/bash
```

* Create two docker volumes for use with the container (contains state)

```powershell
docker volume create sc4s-config
docker volume create sc4s-buffer
```

* Pull the docker container
```powershell
docker pull splunk/scs:latest
```

## Configure the SC4S environment

* Create a folder ```c:\sc4s``` and create a file using notepad

```powershell
mkdir c:\sc4s
notepad c:\sc4s\env_file
```

File contents

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

## Modify index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that are suitable for most customers. 


* If changes need to be made to index destinations enter the container using a docker shell

```powershell
docker exec -it SC4S /bin/bash
```

* Change the the configuration directory ```cd /opt/syslog-ng/etc/conf.d/local/context```

* Edit `splunk_index.csv` to review or change the index configuration and revise as required for the data sources utilized in your
environment. Simply uncomment the relevant line and enter the desired index.  The "Sources" document details the specific entries in
this table that pertain to the individual data source filters that are included with SC4S.

```bash
vi splunk_index.csv
```

Note: locate the position the file to edit use the letter 'i' to enter insert mode to save and exit press esc + ':wq' to abort use esc + ':q!'

## Configure source filtering by source IP or host name

* Change the the configuration directory ```cd /opt/syslog-ng/etc/conf.d/local/context```

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources that require this step, refer to the "sources" section of this documentation. 

* Navigate to `vendor_product_by_source.conf` and find the appropriate filter that matches your legacy device type.  
* Edit the file to properly identify these products by hostname glob or network mask using syslog-ng filter syntax.  Configuration by hostname or source IP is needed only for those devices that cannot be determined via normal syslog-ng parsing or message contents. 
* The `vendor_product_by_source.csv` file should not need to be changed unless a local filter is created that is specific to the environment.  In this case, a matching filter will also need to be provided in `vendor_product_by_source.conf`.

## Configure compliance index/metadata overrides

In some cases, devices that have been properly sourcetyped need to be further categorized by compliance, geography, or other criterion.
The two files `compliance_meta_by_source.conf` and `compliance_meta_by_source.csv` can be used for this purpose.  These operate similarly to
the files above, where the `conf` file specifies a filter to uniquely identify the messages that should be overridden, and the `csv` file
lists one or more metadata items that can be overridden based on the filter name.  This is an advanced topic, and further information is in
the "Configuration" section.

## Start SC4S

```powershell
docker run -d -p 514:514 -p 514:514/udp --restart unless-stopped --env-file=c:\sc4s\env_file -v sc4s-config:/opt/syslog-ng/etc/conf.d/local -v sc4s-buffer:/opt/syslog-ng/var/data/dis-buffer --name SC4S splunk/scs:latest
```

# Configure Dedicated Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.  
For collection of such sources we provide a means of dedicating a unique listening port to a specific source.

Refer to the "Sources" documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example ``-p 5000-5020:5000-5020`` allows for up to 21 technology-specific tcp ports.  Modify individual ports or a
range as appropriate for your network.

* Modify the following file ``/opt/sc4s/env_file`` to include the port-specific environment variable(s). See the "Sources" 
section for more information on your specific device(s).

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example below.

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Restart SC4S (below)

# Restart SC4S

* Modify the docker run command above to include additional ports for example:

```powershell
docker stop SC4S
docker container rm SC4S
docker run -d -p 514:514 -p 514:514/udp -p 5000-5020:5000-5020 --restart unless-stopped --env-file=c:\sc4s\env_file -v sc4s-config:/opt/syslog-ng/etc/conf.d/local -v sc4s-buffer:/opt/syslog-ng/var/data/dis-buffer --name SC4S splunk/scs:latest
```

# Verify Proper Operation

SC4S has a number of "preflight" checks to ensure that the container starts properly and that the syntax of the underlying syslog-ng
configuration is correct.  After this step completes, to verify SC4S is properly communicating with Splunk,
execute the following search in Splunk:

```ini
index=* sourcetype=sc4s:events "starting up"
```
This should yield the following event:
```ini
syslog-ng starting up; version='3.22.1'
``` 
when the startup process proceeds normally (without syntax errors). If you do not see this,
follow the steps below before proceeding to deeper-level troubleshooting:

* Check to see that the URL, token, and TLS/SSL settings are correct, and that the appropriate firewall ports are open (8088 or 443).

* Check to see that the proper indexes are created in Splunk, and that the token has access to them.

* Ensure the proper operation of the load balancer if used.

* Lastly, execute the following command to check the internal logs of the syslog-ng process running in the container.  Depending on the
traffic load, there may be quite a bit of output in the syslog-ng logs.
```bash
docker logs SC4S
```
You should see events similar to those below in the output:
```ini
Oct  1 03:13:35 77cd4776af41 syslog-ng[1]: syslog-ng starting up; version='3.24.1'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection accepted; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection closed; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
```
If you see http server errors such as 4xx or 5xx responses from the http (HEC) endpoint, one or more of the items above are likely set
incorrectly.  If validating/fixing the configuration fails to correct the problem, proceed to the "Troubleshooting" section for more
information.