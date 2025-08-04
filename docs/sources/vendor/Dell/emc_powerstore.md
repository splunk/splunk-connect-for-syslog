# Dell Powerstore

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref            | Link                                                                                                                            |
|----------------|---------------------------------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | N/A                                                                                                                             |
| Add-on Manual  | N/A                                                                                                                             |
| Product Manual | [Powerstore Documentation](https://www.dell.com/support/kbdoc/en-us/000130110/powerstore-info-hub-product-documentation-videos) |

## Sourcetypes

| sourcetype            | notes |
|-----------------------|-------|
| `dell:emc:powerstore` | None  |

### Index Configuration

| key                | sourcetype            | index      | notes                                     |
|--------------------|-----------------------|------------|-------------------------------------------|
| dellemc_powerstore | `dell:emc:powerstore` | `infraops` | Default index changed in version `3.38.0` |

In SC4S `v3.37.0` the data was sent to `netops` index by default. If you want to change the target index, 
you can set the `SC4S_OPTION_DELL_POWERSTORE_INDEX` environment variable to specify a different index name.