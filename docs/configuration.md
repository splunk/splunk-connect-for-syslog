# SC4S Configuration Variables

Other than device filter creation, SC4S is almost entirely controlled by environment variables.  Here are the categories
and variables needed to properly configure SC4S for your environment.

## Global Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SPLUNK_HEC_URL | url | URL(s) of the Splunk endpoint, can be a single URL space seperated list |
| SPLUNK_HEC_TOKEN | string | Splunk HTTP Event Collector Token |


## Splunk HEC Destination Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_WORKERS | numeric | Number of destination workers (threads).  Set this to the number of HEC endpoints up to a max of 32. |
| SC4S_DEST_SPLUNK_HEC_TLS_VERIFY | yes(default) or no | verify HTTP(s) certificate |
| SC4S_DEST_SPLUNK_HEC_CIPHER_SUITE | comma separated list | Open SSL cipher suite list |
| SC4S_DEST_SPLUNK_HEC_SSL_VERSION |  comma separated list | Open SSL version list |
| SC4S_DEST_SPLUNK_HEC_TLS_CA_FILE | path | Custom trusted cert file |

## Syslog Source Configuration

| Variable | Values/Default | Description |
|----------|----------------|-------------|
| SC4S_SOURCE_TLS_ENABLE | no(default) or yes | Enable a TLS listener on port 6514 |
| SC4S_SOURCE_TLS_OPTIONS | See openssl | List of SSl/TLS protocol versions to support | 
| SC4S_SOURCE_TLS_CIPHER_SUITE | See openssl | List of Ciphers to support |
| SC4S_SOURCE_TCP_MAX_CONNECTIONS | 2000 | Max number of TCP Connections |
| SC4S_SOURCE_TCP_IW_SIZE | 20000000 | Initial Window size |
| SC4S_SOURCE_TCP_FETCH_LIMIT | 2000 | Number of events to fetch from server buffer at once |
| SC4S_SOURCE_UDP_SO_RCVBUFF | 425984 | UDP server buffer size in bytes |


## Syslog Source TLS Certificate Configuration

* Create a folder ``/opt/sc4s/tls``
* Save the server private key in PEM format with NO PASSWORD to ``/opt/sc4s/tls/server.key``
* Save the server certificate in PEM format to ``/opt/sc4s/tls/server.pem``
* Add the following line to ``/opt/sc4s/env_file``

```dotenv
SC4S_SOURCE_TLS_ENABLE=yes
```

## Override index or metadata based on host, ip, or subnet

In some cases it is appropriate to re-direct events to an alternate index or append metadata (such as an
indexed field) based on PCI scope, geography, or other criterion.  This is accomplished by the use
of a file that uniquely identifies these source exceptions via syslog-ng filters,
which maps to an associated lookup of alternate indexes, sources, or other metadata.

* Get the filter and lookup files
```bash
cd /opt/sc4s/default
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/compliance_meta_by_source.conf
sudo wget https://raw.githubusercontent.com/splunk/splunk-connect-for-syslog/master/package/etc/context-local/compliance_meta_by_source.csv
```
* Edit the file ``compliance_meta_by_source.conf`` to supply uniquely named filters to identify events subject to override.
* Edit the file ``compliance_meta_by_source.csv``  to supply appropriate the field(s) and values.
The three columns in the table are `filter name`, `field name`, and `value`.  `field name` obeys the following convention:
    * ``fields.fieldname`` where `fieldname` will become the name of an indexed field with the supplied value
    * ``.splunk.index`` to specify an alternate value for index
    * ``.splunk.source`` to specify an alternate value for source 
    
* For the Docker/Podman runtimes, update the docker/podman run command in the systemd unit file or the docker-compose to
include volumes mapping the files above.
* In the Unit file, add the following lines to the `ExecStart` command prior to `$SC4SIMAGE` then restart using the command
``sudo systemctl daemon-reload; sudo systemctl restart sc4s``

``
SC4S_UNIT_VP_CSV=-v /opt/sc4s/default/compliance_meta_by_source.csv:/opt/syslog-ng/etc/context-local/compliance_meta_by_source.csv \
SC4S_UNIT_VP_CONF=-v /opt/sc4s/default/compliance_meta_by_source.conf:/opt/syslog-ng/etc/context-local/compliance_meta_by_source.conf \
``

* For the Docker Swarm runtime, update the docker compose yml to add the following volume mounts to thee sc4s service and
redeploy the updated service using the command:
``docker stack deploy --compose-file docker-compose.yml sc4s``
 
``
      - /opt/sc4s/default/compliance_meta_by_source.csv:/opt/syslog-ng/etc/context-local/compliance_meta_by_source.csv
      - /opt/sc4s/default/compliance_meta_by_source.conf:/opt/syslog-ng/etc/context-local/compliance_meta_by_source.conf
``
## Data Durability - Local Disk Buffer Configuration

SC4S provides capability to minimize the number of lost events if the connection to all the Splunk Indexers goes down. This capability utilizes the disk buffering feature of Syslog-ng. SC4S receives a response from the Splunk HTTP Event Collector (HEC) when a message is received successfully. If a confirmation message from the HEC endpoint is not received (or a “server busy” reply, such as a “503” is sent), the load balancer will try the next HEC endpoint in the pool.  If all pool members are exhausted (such as would occur if there were a full network outage to the HEC endpoints), events will queue to the local disk buffer on the SC4S Linux host. SC4S will continue attempting to send the failed events while it buffers all new incoming events to disk. If the disk space allocated to disk buffering fills up then SC4S will stop accepting new events and subsequent events will be lost. Once SC4S gets confirmation that events are again being received by one or more indexers, events will then stream from the buffer using FIFO queueing. The number of events in the disk buffer will reduce as long as the incoming event volume is less than the maximum SC4S (with the disk buffer in the path) can handle. When all events have been emptied from the disk buffer, SC4S will resume streaming events directly to Splunk. 

For more detail on the Syslog-ng behavior the documentation can be found here: https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/3.22/administration-guide/55#TOPIC-1209280

SC4S has disk buffering enabled by default and it is strongly recommended that you keep it on, however this feature does have a performance cost. 
Without disk buffering enabled SC4S can handle up to 345K EPS (800 bytes/event avg)
With “Normal” disk buffering enabled SC4S can handle up to 60K EPS (800 bytes/event avg) -- This is still a lot of data!

To guard against data loss it is important to configure the appropriate type and amount of storage for SC4S disk buffering. To estimate the storage allocation its best to start with your estimated maximum events per second that each SC4S server will experience. Based on the maximum throughput of SC4S with disk buffering enabled, the conservative estimate for maximum events per second is 60K (however, you should use the maximum rate in your environment for this calculation, not the max rate SC4S can handle). Next is your average estimated event size based on your data sources. It is common industry practice to estimate log events as 800 bytes on average. And the final input to the sizing estimation would be the maximum length of connectivity downtime you want disk buffering to be able to handle. This measure is very much dependent on your risk tolerance. For example, to protect against a full day of lost connectivity from SC4S to all your indexers at maximum throughput the calculation would look like the following...

60,000 EPS * 86400 seconds * 800 bytes = 3.77186 TB of storage

To configure storage allocation for the SC4S disk buffering, do the following...
Edit the file /opt/sc4s/default/env_file
Add the SC4S_DEST_SPLUNK_HEC_DISKBUFF_DISKBUFSIZE variable to the file and set the value to the number of bytes based on your estimation (e.g. 4147200000000 in the example above)
Splunk does not recommend reducing the disk allocation below 500 GB
Restart SC4S

Given that in a connectivity outage to the Indexers events will be saved and read from disk until the buffer is emptied, it is ideal to use the fastest type of storage available. For this reason, NVMe storage is recommended for SC4S disk buffering.
