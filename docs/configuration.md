# Global Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SPLUNK_HEC_URL | url | URL(s) of the Splunk endpoint, can be a single URL space seperated list |
| SPLUNK_HEC_TOKEN | string | Splunk HTTP Event Collector Token |


# Splunk HEC destination Configuration

| Variable | Values        | Description |
|----------|---------------|-------------|
| SC4S_DEST_SPLUNK_HEC_TLS_VERIFY | yes(default) or no | verify HTTP(s) certificate |
| SC4S_DEST_SPLUNK_HEC_CIPHER_SUITE | comma separated list | Open SSL cipher suite list |
| SC4S_DEST_SPLUNK_HEC_SSL_VERSION |  comma separated list | Open SSL version list |
| SC4S_DEST_SPLUNK_HEC_TLS_CA_FILE | path | Custom trusted cert file |

# Syslog Source Configuration

| Variable | Values/Default | Description |
|----------|----------------|-------------|
| SC4S_SOURCE_TLS_ENABLE | no(default) or yes | Enable a TLS listener on port 6514 |
| SC4S_SOURCE_TLS_OPTIONS | See openssl | List of SSl/TLS protocol versions to support | 
| SC4S_SOURCE_TLS_CIPHER_SUITE | See openssl | List of Ciphers to support |
| SC4S_SOURCE_TCP_MAX_CONNECTIONS | 2000 | Max number of TCP Connections |
| SC4S_SOURCE_TCP_IW_SIZE | 20000000 | Initial Window size |
| SC4S_SOURCE_TCP_FETCH_LIMIT | 2000 | Number of events to fetch from server buffer at once |
| SC4S_SOURCE_UDP_SO_RCVBUFF | 425984 | UDP server buffer size in bytes |


# Syslog Source TLS Certificate Configuration

* Create a folder ``/opt/sc4s/tls``
* Save the server private key in PEM format with NO PASSWORD to ``/opt/sc4s/tls/server.key``
* Save the server certificate in PEM format to ``/opt/sc4s/tls/server.pem``
* Add the following line to ``/opt/sc4s/default/env_file``

```dotenv
SC4S_SOURCE_TLS_ENABLE=yes
```

