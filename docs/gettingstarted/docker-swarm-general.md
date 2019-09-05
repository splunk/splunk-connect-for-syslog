
# Install Docker CE and Swarm

Refer to [Getting Started](https://docs.docker.com/get-started/)

# Setup

* Create a directory on the server for configuration this should be available to all administrators for example
``/opt/scs/``
* Create a docker-compose.yml file based on the following template

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
    environment:
      - SPLUNK_HEC_URL=https://inputs-hec.kops.spl.guru/services/collector/event
      - SPLUNK_HEC_TOKEN=02450979-d363-4e6c-b6c9-796d8b546a6e
      - SPLUNK_CONNECT_METHOD=hec
      - SPLUNK_DEFAULT_INDEX=main
      - SPLUNK_METRICS_INDEX=em_metrics
    volumes:
#Uncomment the following line if overriding index destinations    
#      - ./sc4s-juniper/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
#Uncomment the following lines if using a host or network based filter and log_path
#      - ./sc4s-juniper/vendor_product_by_source.csv:/opt/syslog-ng/etc/context-local/vendor_product_by_source.csv
#      - ./sc4s-juniper/vendor_product_by_source.conf:/opt/syslog-ng/etc/context-local/vendor_product_by_source.conf

```

## Configure index destinations for Splunk 

Log paths are preconfigured to utilize a convention of index destinations that is suitable for most customers. This step is optional to allow customization of index destinations.

* Download the latest context.csv file to a subdirectory sc4s below the docker-compose.yml file created above

```bash
wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

## Configure sources by source IP or host name

Legacy sources and non-standard compliant source require configuration by source IP or hostname as included in the event the following steps apply to support such sources. To identify sources which require this step refer to the sources section of this documentation. 

* Download the latest vendor_product_by_source.conf file to a subdirectory sc4s below the docker-compose.yml file created above
```bash
wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/vendor_product_by_source.conf
```
* Edit the file to identify appropriate vendor products by host glob or network mask using syslog-ng filter syntax.

* Start SC4S

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```


## Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations


## Single Source Technology instance - Alpha

For certain source technologies message categorization by content is impossible to support collection 
of such legacy nonstandard sources we provide a means of dedicating a container to a specific source using
an alternate port. In the following configration example a dedicated port is opened (6514) for legacy juniper netscreen devices

This approach is "alpha" and subject to change

```yaml
version: "3"
services:
  sc4s-juniper-netscreen:
    image: splunk/scs:latest
    hostname: sc4s-juniper-netscreen
    ports:  
       - target: 514
         published: 6514
         protocol: tcp
#Comment the following line out if using docker-compose
         mode: host
       - target: 514
         published: 6514
         protocol: udp
#Comment the following line out if using docker-compose         
         mode: host
    environment:
      - SPLUNK_HEC_URL=https://foo:8088/services/collector/event
      - SPLUNK_HEC_TOKEN=<token>
      - SPLUNK_CONNECT_METHOD=hec
      - SPLUNK_DEFAULT_INDEX=<defaultindex>
      - SPLUNK_METRICS_INDEX=em_metrics
      - SYSLOG_PRESUME_FILTER=f_juniper_netscreen
    volumes:
    - ./sc4s-juniper/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
```