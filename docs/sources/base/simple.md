# Simple Log path by port

The SIMPLE source configuration allows configuration of a log path for SC4S using a single port
to a single index/sourcetype combination to quickly onboard new sources that have not been formally
supported in the product. Source data must use RFC5424 or a common variant of RFC3164 formatting.

* NOTE:  This is an _interim_ step that should be used only to quickly onboard well-formatted data that is being sent over a
unique port.  A dedicated log path should be developed for the data source to facilitate further parsing and enrichment, as
well as allowing the potential sending of this data source over the default (514) listening port.

## Splunk Metadata with SIMPLE events

The keys (first column) in `splunk_metadata.csv` for SIMPLE data sources is a user-created key using the `vendor_product` convention.
For example, to on-board a new product `first firewall` using a source type of `first:firewall` and index `netfw`, add the following
two lines to the configuration file as shown:

```
first_firewall,index,netfw
first_firewall,sourcetype,first:firewall
```

## Options

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

* `SIMPLE` data sources must use RFC5424 or a common variant of RFC3164 formatting.
* Each `SIMPLE` data source must listen on its own unique port list.  Port overlap with other
sources, either `SIMPLE` ones or those served by regular log paths, are not allowed and will cause an error at startup.
* The key(s) chosen for `splunk_metadata.csv` must be in the form `vendor_product` (lower case).
* These same keys can be used for a regular SC4S log path developed in the future.
* The `SIMPLE` environment variables must have a core of `VENDOR_PRODUCT` (upper case).
* Take care to remove the `SIMPLE` form of these `LISTEN` variables after a regular SC4S log path is developed for
a given source. You can, of course, continue to listen for this source on the same unique ports after having developed
the new log path, but use the `SC4S_LISTEN_<VENDOR_PRODUCT>_<protocol>_PORT` form of the variable to ensure the newly
developed log path will listen on the specified unique ports.
