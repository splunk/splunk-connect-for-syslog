
# Pre-req

* Linux host with 4-6 cores & 2-4 GB memory (Docker container should be allocated 2 cores 2 GB of memory) and Docker 19.x or newer with Docker Swarm enabled
    * [Getting Started](https://docs.docker.com/get-started/)
* A Splunk index for metrics typically "em_metrics"
* One or more Splunk indexes for events collected by SC4S
* Splunk HTTP event collector enabled with a token dedicated for SC4S
    * [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q)
    * [Splunk Enterprise Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)
* A network load balancer (NLB) configured for round robin. Note: Special consideration may be required when more advanced products are used. The optimal configuration of the load balancer will round robin each http POST request (not each connection)

# Setup

* Create a directory on the server for configuration
* Create a docker-compose.yml file based on the following template

```yaml
version: "3"
services:
  sc4s:
    image: splunk/scs:latest
    hostname: sc4s
    ports:
      - "514:514"
      - "601:601"
      - "514:514/udp"
      - "5514:5514"
      - "5514:5514/udp"
    stdin_open: true
    tty: true
    environment:
      - SPLUNK_HEC_URL=https://foo:8088/services/collector/event
      - SPLUNK_HEC_TOKEN=<token>
      - SPLUNK_CONNECT_METHOD=hec
      - SPLUNK_DEFAULT_INDEX=<defaultindex>
      - SPLUNK_METRICS_INDEX=em_metrics
    volumes:
    - ./sc4s/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
    - ./sc4s/splunk_index.csv:/opt/syslog-ng/etc/context-local/splunk_index.csv
```

## Configure index destinations for Splunk 
* Download the latest context.csv file to a subdirectory sc4s below the docker-compose.yml file created above
```bash
wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/splunk_index.csv
```
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

## Configure sources by source IP or host name
* This step is required even if not used
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
      - "6514:514"
      - "6514:514/udp"
    stdin_open: true
    tty: true
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
