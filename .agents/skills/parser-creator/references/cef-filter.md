Here is an example of a CEF filter (replace values inside `<>` with your own):

```
application app-cef-<device_vendor>_<device_product>[cef] {
    filter{
        match("<device_vendor>" value(".metadata.cef.device_vendor"))
        and match("<device_product>" value(".metadata.cef.device_product"));
    };
    parser { app-cef-<device_vendor>_<device_product>(); };
};
```


<!-- DEPRECATED:

block parser app-cef-<device_vendor>_<device_product>() {
    channel {
        rewrite {
            r_set_splunk_dest_default(
                index('<index>'),
                source('<device_vendor>:<device_product>'),
                sourcetype('<device_vendor>:<device_product>:cef')
                vendor('<device_vendor>')
                product('<device_product>')
            );
        };
    };
}; -->
