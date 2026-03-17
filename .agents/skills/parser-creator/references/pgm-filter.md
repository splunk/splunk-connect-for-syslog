Here is an example of a `pgm` filter (replace values inside `<>` with your own):

```
application app-syslog-<vendor_name>_<product_name>[sc4s-syslog-pgm] {
	filter {
        program('<program>' type(string) flags(prefix));
    };	
    parser { <parser-name>(); };
};
```

