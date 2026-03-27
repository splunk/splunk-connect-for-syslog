# SC4S parsers

!!! note "Prerequisites"
    Before reading this section, make sure you are familiar with [Sources](sources).

This and subsequent sections describe how to create new parsers. SC4S parsers perform operations that would normally be performed during index time, including line-breaking, source and sourcetype setting. You can write your own parser if the parsers available in the SC4S package do not meet your needs or you want to add support for new sourcetype.

## Before you start

* Make sure you have read our [contribution standards](CONTRIBUTING.md).
* Create a new branch in the repository where you will apply your changes.
* Obtain a raw log message that you want to parse. If you don't know how to do it, refer to [Obtain raw message events](../troubleshooting/troubleshoot_resources.md#obtain-raw-message-events).
* Prepare your testing environment. With Python>=3.11.0:

```
pip3 install poetry
poetry install
```

## Parsers

### Naming conventions and project structure

Parsers are .conf files with the naming convention: `app-type-vendor_product.conf`. In the repository, the parsers should be put in `package/etc/conf.d/conflib` directory for the main package. For SC4S lite, parsers are grouped into `addons`. Create a folder (if it doesn't already exist) in `package/lite/etc/addons` with the name of vendor. In this folder also create an `addon_metadata.yaml` file with vendor name:

```
---
name: "<vendor_name>"
```

Lastly, add this addon to `package/lite/etc/config.yaml`.

### Parser structure

The SC4S parser consists of `application` and `block parser` blocks. The `application` part uses filter clause to specify what logs will be parsed by the `block parser` block. Example of such parser is shown below:

```
--8<---- "docs/resources/parser_development/app-syslog-vmware_cb-protect_example_basic.conf"
```

!!! note "Note"
     If you find a similar parser in SC4S, you can use it as a reference. In the parser, make sure you assign the proper sourcetype, index, vendor, product, and template. The template shows how your message should be parsed before sending them to Splunk.


The application filter will match all messages that start with the string `Carbon Black App Control event:`, and those events will be parsed by `block parser app-syslog-vmware_cb-protect()`. This parser then will route the message to index: `epintel`, set the sourcetype, source, vendor and product fields, and use speciefed template.

![](../resources/images/parser_dev_basic_output.png)

To learn more about creating filters and parse blocks see pages: [Filter Messages](filter_message) and [Parse Messages](parse_message).