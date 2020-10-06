# Vendor - Neutral Simple Log path by port

## Product - multiple

The SIMPLE source configuration allows configuration of a log path to Splunk using a single port
to a single index + source type as a way of quickly onboarding new sources that have not been formally
supported in the product. Sources must use RFC5424 or a common variant of RFC3164


### Splunk Metadata with SIMPLE events

The keys (first column) in `splunk_metadata.csv` for SIMPLE data sources is a user created key for example if I was to on-board a 
new product 'first firewall' using a source type of `first:firewall` and index `netfw` I would add the following two lines to the configuration file
note: the key must be lower case
```
simple_first_firewall,index,netfw
simple_first_firewall,sourcetype,first:firewall
```

### Options

Replace 'VENDOR_PRODUCT' with the values used in the `splunk_metadata.csv` file for our example above to establish a tcp listener for first firewall we would use
`SC4S_LISTEN_SIMPLE_FIRST_FIREWALL_TCP_PORT` note vendor product must be upper case.

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SIMPLE_VENDOR_PRODUCT_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_SIMPLE_VENDOR_PRODUCT_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_SIMPLE_VENDOR_PRODUCT_TLS_PORT      | empty string      | Enable a TLS  port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_SIMPLE_VENDOR_PRODUCT | no | Enable archive to disk for this specific source |
| SC4S_DEST_SIMPLE_VENDOR_PRODUCT_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

