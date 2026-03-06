Example of an `sc4s-syslog` topic filter:

```
application app-syslog-<vendor_name>_<vendor_product>[sc4s-syslog] {
	filter {
        message('Carbon Black App Control event:  '  type(string)  flags(prefix));
    };	
    parser { <parser-name>(); };
};
```