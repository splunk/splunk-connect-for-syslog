
# Install Docker CE and Swarm

Refer to [Getting Started](https://docs.docker.com/get-started/)

# SC4S Configuration

* Create a directory on the server for local configurations. This should be available to all administrators, for example:
``/opt/sc4s/``
* Create a docker-compose.yml file in the directory created above, based on the following template:

```yaml
version: "3.7"
services:
  sc4s:
    image: splunk/scs:latest
    ports:  
       - target: 514
         published: 514
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
       - target: 514
         published: 514
         protocol: udp
#Comment the following line out if using docker-compose         
         mode: host
    env_file:
      - /opt/sc4s/env_file
    volumes:
      - /opt/sc4s/default/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
      - /opt/sc4s/default/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv
      - /opt/sc4s/default/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf
#Uncomment the following line if custom TLS certs are provided
      - /opt/sc4s/tls:/opt/syslog-ng/tls
```

* NOTE:  If you use the default `volumes` declarations as-is from the `docker-compose.yml` file template example, you must create and/or download all files and directories referenced in the file according to the configuration steps that follow.  The TLS-specific options are described in the "Configure the sc4s Environment" section. Failure to match the volume specification in the `yml` file with what exists locally will result in startup errors.

## Configure the SC4S environment

Create a file named ``/opt/sc4s/env_file`` and add the following environment variables:

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment.

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example above.

## Configure index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that is suitable for most customers. 

* Create a subdirectory called ``default`` in the directory that you created in the previous step (e.g. ``/opt/sc4s/``). Make sure the local directory volume references in the `yml` file match the directory you create here.  From this directory,
execute the command below to download the index context file:

```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv to review the index configuration and revise as required for the sourcetypes utilized in your environment.

## Configure sources by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps
apply to support such sources. To identify sources that require this step, refer to the "sources" section of this documentation. 

* If not already done, create a subdirectory called ``default`` in the ``/opt/sc4s/`` directory. Make sure the local directory volume references in the `yml` file match the directory you create here. From this directory, execute the following commands to download the vendor context files:

```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.conf
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.csv
```
* If you have legacy sources and non-standard-compliant sources, edit the file to properly identify these products by host glob or network mask using syslog-ng filter syntax.

## Start/Restart SC4S

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```

# Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations.


# Configure Dedicated Listening Ports

For certain source technologies, categorization by message content is impossible due to the lack of a unique "fingerprint" in
the data.  In other cases, a unique listening port is required for certain devices due to network requirements in the enterprise.  
For collection of such sources we provide a means of dedicating a unique listening port to a specific source.

Refer to the "Sources" documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example ``-p 5000-5020:5000-5020`` allows for up to 21 technology-specific ports.  Modify the individual ports or a
range as appropriate for your network.

* Modify the unit file ``/opt/sc4s/docker-compose.yml``
```yaml
version: "3.7"
services:
  sc4s:
    image: splunk/scs:latest
    ports:  
       - target: 514
         published: 514
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
       - target: 514
         published: 514
         protocol: udp
#Comment the following line out if using docker-compose         
         mode: host
       - target: 5000-5021
         published: 5000-5021
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
       - target: 5000-5021
         published: 5000-5021
         protocol: udp
#Comment the following line out if using docker-compose         
         mode: host
    env_file:
      - /opt/sc4s/env_file
    volumes:
      - /opt/sc4s/default/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
      - /opt/sc4s/default/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv
      - /opt/sc4s/default/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf
#Uncomment the following line if custom TLS certs are provided
      - /opt/sc4s/tls:/opt/syslog-ng/tls
```

* Modify the following file ``/opt/sc4s/default/env_file`` to include the port-specific environment variable(s).  See the "Sources" 
section for more information on your specific device(s).

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

* Set `SC4S_DEST_SPLUNK_HEC_WORKERS` to match the number of indexers and/or HWFs with HEC endpoints.  If the endpoint is a VIP,
match this value to the total number of indexers behind the load balancer.

* NOTE:  Splunk Connect for Syslog defaults to secure configurations.  If you are not using trusted SSL certificates, be sure to
uncomment the last line in the example below.

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SC4S_DEST_SPLUNK_HEC_WORKERS=6
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
SC4S_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
#Uncomment the following line if using untrusted SSL certificates
#SC4S_DEST_SPLUNK_HEC_TLS_VERIFY=no
```

* Restart SC4S (below)

## Start/Restart SC4S

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```

# Stop SC4S

Start by obtaining the stack name (ID):
```bash
docker stack ls
```
Then, remove the stack:
```bash
docker stack rm <ID>
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
Oct  1 03:13:35 77cd4776af41 syslog-ng[1]: syslog-ng starting up; version='3.22.1'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection accepted; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
Oct  1 05:29:55 77cd4776af41 syslog-ng[1]: Syslog connection closed; fd='49', client='AF_INET(10.0.1.18:55010)', local='AF_INET(0.0.0.0:514)'
```
If you see http server errors such as 4xx or 5xx responses from the http (HEC) endpoint, one or more of the items above are likely set
incorrectly.  If validating/fixing the configuration fails to correct the problem, proceed to the "Troubleshooting" section for more
information.
