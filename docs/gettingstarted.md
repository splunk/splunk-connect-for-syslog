
# Pre-req

* Linux host with Docker 19.x or newer with Docker Swarm enabled
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
      - "514"
      - "601"
      - "514/udp"
      - "5514"
      - "5514/udp"
    stdin_open: true
    tty: true
    environment:
      - SPLUNK_HEC_URL=https://foo:8088/services/collector/event
      - SPLUNK_HEC_TOKEN=<token>
      - SPLUNK_CONNECT_METHOD=hec
      - SPLUNK_DEFAULT_INDEX=<defaultindex>
      - SPLUNK_METRICS_INDEX=em_metrics
    volumes:
    - splunk_index.csv:/opt/syslog-ng/etc/context/splunk_index.csv
```

* Download the latest context.csv file to the current directory
```bash
wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context/splunk_index.csv
```

* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment.

* Start SC4S

```bash
docker stack deploy --compose-file docker-compose.yml sc4s
```


## Scale out

Additional hosts can be deployed for syslog collection from additional network zones and locations
