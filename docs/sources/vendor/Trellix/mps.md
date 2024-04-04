# Trellix MPS

## Key facts

* MSG Format based filter
* Legacy BSD Format default port 514

## Links

| Ref                                   | Link                                                                             |
|---------------------------------------|----------------------------------------------------------------------------------|
| Splunk Add-on                         | None                                                                             |


## Sourcetypes

| sourcetype                  | notes                                                                                      |
|-----------------------------|--------------------------------------------------------------------------------------------|
| trellix:mps                 | CEF                                                                                        |

## Source

| source               | notes                                                                                             |
|----------------------|---------------------------------------------------------------------------------------------------|
| trellix:mps          | None                                                                                              |

### Index Configuration

| key                | source              | index                  | notes          |
|--------------------|---------------------|------------------------|----------------|
|trellix_mps         | trellix:mps         | netops                 | none           |
