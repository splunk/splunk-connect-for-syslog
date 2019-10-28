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

## Archive File Configuration

This feature is designed to support "compliance" archival of all messages. To enable this feature update the Unit file or docker compose to
mount an appropriate host folder to the container folder ``/opt/syslog-ng/var/archive`` The files will be stored in a folder structure using the
naming pattern ``${YEAR}/${MONTH}/${DAY}/${fields.sc4s_vendor_product}_${YEAR}${MONTH}${DAY}${HOUR}${MIN}.log"``. This pattern will create
one file per "vendor_product" per minute with records formatted using syslog-ng's EWMM template. 


| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_ARCHIVE_GLOBAL | yes or undefined | Enable archive of all vendor_products |
| SC4S_ARCHIVE_LISTEN_<VENDOR_PRODUCT> | yes(default) or undefined | See sources section of documentation enables selective archival |
  

## Syslog Source Configuration

| Variable | Values/Default | Description |
|----------|----------------|-------------|
| SC4S_LISTEN_DEFAULT_TLS_PORT | undefined or 6514 | Enable a TLS listener on port 6514 |
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

