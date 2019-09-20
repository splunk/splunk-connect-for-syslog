
# Install Docker CE and Swarm

*Warning* this method of installing docker on RHEL does not appear to be supported:

Enable required repositories
```bash
subscription-manager repos --enable=rhel-7-server-rpms
subscription-manager repos --enable=rhel-7-server-extras-rpms
subscription-manager repos --enable=rhel-7-server-optional-rpms
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

Enable EPEL
```bash
yum install wget -y
cd /tmp
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
rpm -Uvh epel-release-latest-7.noarch.rpm
```

Install required packages and enable docker
```bash
yum install docker-ce -y
systemctl enable docker.service
systemctl start docker.service
```

Initialize Docker Swarm
```bash
sudo docker swarm init
```

# Setup

* Create a directory on the server for configuration. This should be available to all administrators, for example:
``/opt/scs/``
* Create a docker-compose.yml file and place it in the directory created above based on the following template:

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
      - /opt/scs/env_file
    volumes:
#Uncomment the following line if overriding index destinations    
#      - ./sc4s-juniper/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
#Uncomment the following lines if using a host or network based filter and log_path
#      - ./sc4s-juniper/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv
#      - ./sc4s-juniper/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf

```

## Configure the SCS environment

Create the following file ``/opt/scs/env_file``

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
```


## Configure index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that is suitable for most customers. This step is optional to allow customization of index destinations.

* Download the latest context.csv file to a subdirectory sc4s below the docker-compose.yml file created above.

```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

## Configure sources by source IP or host name

Legacy sources and non-standard-compliant sources require configuration by source IP or hostname as included in the event. The following steps apply to support such sources. To identify sources which require this step refer to the "sources" section of this documentation. 

* Download the latest vendor_product_by_source.conf file to a subdirectory sc4s below the docker-compose.yml file created above
```bash
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.conf
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.csv
```
* Edit the file to identify appropriate vendor products by host glob or network mask using syslog-ng filter syntax.

* Start SC4S.

```bash
sudo docker stack deploy --compose-file docker-compose.yml sc4s
```

## Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations.


# Single Source Technology instance

For certain source technologies message categorization by content is impossible to support collection 
of such legacy nonstandard sources we provide a means of dedicating a container to a specific source using
an alternate port. 
Refer to the Sources documentation to identify the specific variable used to enable a specific port for the technology in use.

In the following example ``-p 5000-5020:5000-5020`` allows for up to 21 technology specific ports modify the range as appropriate

* Modify the unit file ``/opt/scs/docker-compose.yml``
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
      - /opt/scs/env_file
    volumes:
#Uncomment the following line if overriding index destinations    
#      - ./sc4s-juniper/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
#Uncomment the following lines if using a host or network based filter and log_path
#      - ./sc4s-juniper/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv
#      - ./sc4s-juniper/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf
```

Modify the following file ``/opt/scs/default/env_file`` 

* Update ``SPLUNK_HEC_URL`` and ``SPLUNK_HEC_TOKEN`` to reflect the correct values for your environment

```dotenv
SPLUNK_HEC_URL=https://splunk.smg.aws:8088/services/collector/event
SPLUNK_HEC_TOKEN=a778f63a-5dff-4e3c-a72c-a03183659e94
SPLUNK_CONNECT_METHOD=hec
SPLUNK_DEFAULT_INDEX=main
SPLUNK_METRICS_INDEX=em_metrics
SCS_LISTEN_JUNIPER_NETSCREEN_TCP_PORT=5000
#Uncomment the following line if using untrusted SSL certificates
#SCS_DEST_SPLUNK_HEC_TLS_VERIFY=no
```
* Start SC4S.

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```
