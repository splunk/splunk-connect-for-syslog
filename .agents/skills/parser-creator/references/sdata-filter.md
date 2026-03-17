Example of an `sdata` filter:

```
application app-syslog-<vendor_name>_<product_name>[sc4s-syslog-sdata] {
    filter {
        match('@<PEN>' value("SDATA"));
    };
    parser { <parser-name>(); };
};
```