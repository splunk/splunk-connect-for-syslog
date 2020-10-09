# Vendor - Neutral Simple Log path by port

## Product - multiple

The SIMPLE source configuration allows configuration of a log path for SC4S using a single port
to a single index/sourcetype combintation to quickly onboard new sources that have not been formally
supported in the product. Source data must use RFC5424 or a common variant of RFC3164 formatting.

* NOTE:  This is an _interim_ step that should be used only to quickly onboard well-formatted data that is being sent over a
unique port.  A dedicated log path should be developed for the data source to facilitate further parsing and enrichment, as
well as allowing the potential sending of this data source over the default (514) listening port.


### Splunk Metadata with SIMPLE events

The keys (first column) in `splunk_metadata.csv` for SIMPLE data sources is a user-created key using the `vendor_product` convention.
For example, to on-board a new product `first firewall` using a source type of `first:firewall` and index `netfw`, add the following
two lines to the configuration file as shown:
```
simple_first_firewall,index,netfw
simple_first_firewall,sourcetype,first:firewall
```

### Options

For the variables below, replace `VENDOR_PRODUCT` with the key (converted to upper case) used in the `splunk_metadata.csv`.
Based on the example above, to establish a tcp listener for `first firewall` we would use `SC4S_LISTEN_SIMPLE_FIRST_FIREWALL_TCP_PORT`.

| Variable       | default        | description    |
|----------------|----------------|----------------|
| SC4S_LISTEN_SIMPLE_VENDOR_PRODUCT_UDP_PORT      | empty string      | Enable a UDP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_SIMPLE_VENDOR_PRODUCT_TCP_PORT      | empty string      | Enable a TCP port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_LISTEN_SIMPLE_VENDOR_PRODUCT_TLS_PORT      | empty string      | Enable a TLS  port for this specific vendor product using a comma-separated list of port numbers |
| SC4S_ARCHIVE_SIMPLE_VENDOR_PRODUCT | no | Enable archive to disk for this specific source |
| SC4S_DEST_SIMPLE_VENDOR_PRODUCT_HEC | no | When Splunk HEC is disabled globally set to yes to enable this specific source | 

### Important Notes

* Source data must use RFC5424 or a common variant of RFC3164 formatting.
* the key(s) chosen for `splunk_metadata.csv` must be in the form `vendor_product` (lower case).
* The environment variables must have a core of `VENDOR_PRODUCT` (upper case).
