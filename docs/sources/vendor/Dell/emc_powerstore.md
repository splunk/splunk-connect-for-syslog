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

| key                | sourcetype            | index      | notes |
|--------------------|-----------------------|------------|-------|
| dellemc_powerstore | `dell:emc:powerstore` | `infraops` | none  |

In SC4S `v3.37.0` the data is send to `netops` index by default. If you want to change it back you can use the `SC4S_OPTION_DELL_POWERSTORE_INDEX` environment variable to set the index name.