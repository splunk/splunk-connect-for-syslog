Here is an example of a `netsource` filter:

```
application app-netsource-barracuda_syslog[sc4s-network-source] {
	filter {
        not filter(f_is_source_identified)
        and (
                (
                    match("barracuda", value('.netsource.sc4s_vendor'), type(string)) 
                    and match("syslog", value('.netsource.sc4s_product'), type(string)) 
                )
                or (tags("ns_vendor:barracuda") and tags("ns_product:syslog"))
                or tags(".source.s_BARRACUDA_SYSLOG")
            )
        ;
    };	
    parser { app-netsource-barracuda_syslog(); };
};
```