# Getting Started

Splunk Connect for Syslog is a containerized distribution of syslog-ng with a configuration framework
designed to simplify getting syslog data into Splunk Enterprise and Splunk Cloud. Our approach is
to provide a container runtime agnostic solution allowing customers to follow our guidance or adapt the solution
to their enterprise container strategy.


# Planning Deployment

Syslog is an overloaded term that refers to multiple message formats AND optionally a wire protocol for
transmission of events between computer systems over UDP, TCP, or TLS. The protocol is designed to minimize
overhead on the sender favoring performance over reliability. This fundamental choice means any instability
or resource constraint will cause data to be lost in transmission.

* When practical and cost effective considering the importance of completeness as a requirement, place the scs
instance in the same VLAN as the source device.

* Avoid crossing a Wireless network, WAN, Firewall, Load Balancer, or inline IDS.
* When High Availability of a single instance of SCS is required, implement multi node clustering of the container 
environment.
* Avoid TCP except where the source is unable to contain the event to a single UDP packet.
* Avoid TLS except where the event may cross a untrusted network.


# Implementation

## Setup indexes in Splunk

SCS is pre-configured to map each sourcetype to a typical index, for new installations best practice is to create the following
indexes in Splunk. The indexes can be customized easily if desired. If using defaults create the following indexes on Splunk:

* netauth
* netfw
* netids
* netops
* netproxy
* netipam
* em_metrics (ensure this is created as a metrics index)

## Install Related Splunk Apps

Install the following:

* [Splunk App for Infrastructure](https://splunkbase.splunk.com/app/3975/)
* [Splunk Add-on for Infrastructure](https://splunkbase.splunk.com/app/4217/)
* [Splunk Metrics Workspace](https://splunkbase.splunk.com/app/4192/) *NOTE Included in Splunk 7.3.0 and above* 

## Setup Splunk HTTP Event Collector

- Set up the Splunk HTTP Event Collector with the HEC endpoints behind a load balancer (VIP) configured for https round robin *WITHOUT* sticky session.  Alternatively, a list of HEC endpoint URLs can be configured in SC4S if no load balancer is in place.  In either case, it is recommended that SC4S traffic be sent to HEC endpoints configured directly on the indexers rather than an intermediate tier of HWFs.
- Create a HEC token that will be used by SCS and ensure the token has access to place events in main, em_metrics, and all indexes used as event destinations
 
### Splunk Cloud

Refer to [Splunk Cloud](http://docs.splunk.com/Documentation/Splunk/7.3.1/Data/UsetheHTTPEventCollector#Configure_HTTP_Event_Collector_on_managed_Splunk_Cloud)

### Splunk Enterprise

Refer to [Splunk Enterprise](http://dev.splunk.com/view/event-collector/SP-CAAAE6Q)

## Implement a container run time and SCS

| Container and Orchestration | Notes |
|-----------------------------|-------|
| [Podman + systemd single node](gettingstarted/podman-systemd-general.md) | First choice for RedHat 7.x and 8.x, second choice for Debian and Ubuntu (packages provided via PPA) |
| [Docker CE + systemd single node](gettingstarted/docker-systemd-general.md) | First choice for Debian, Ubuntu, and CentOS distributions with limited existing docker experience |
| [Docker CE + Swarm single node](gettingstarted/docker-swarm-general.md) | Option for Debian, Ubuntu, and CentOS  desiring swarm orchestration |
| [Docker CE + Swarm single node RHEL 7.7](gettingstarted/docker-swarm-rhel7.md) | Option for RedHat 7.7 desiring swarm orchestration |
=======
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
* Edit splunk_index.csv review the index configuration and revise as required for sourcertypes utilized in your environment. For instance, add *cisco:asa,index,netfw* to splunk_index.csv for Cisco-ASA data source.

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

![SC4S deployment diagram](SC4S%20deployment.png)

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