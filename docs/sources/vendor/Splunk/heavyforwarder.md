# Splunk Heavy Forwarder

In certain network architectures such as those using data diodes or those networks requiring "in the clear" inspection at network egress 
SC4S can be used to accept specially formatted output from Splunk as RFC5424 syslog.

## Key facts

* RFC 5424 using port 601 (Framed)

## Links

| Ref            | Link                                                                                                    |
|----------------|---------------------------------------------------------------------------------------------------------|
| Splunk Add-on  | None                                    |
| Product Manual | unknown   |

## Sourcetypes

| sourcetype     | notes                                                                                                   |
|----------------|---------------------------------------------------------------------------------------------------------|
| spectracom:ntp        | None                                                                                                    |
| nix:syslog | None |

## Sourcetype and Index Configuration

Index Source and Sourcetype will be used as determined by the Source/HWF

## Splunk Configuration

* Splunk MUST have props and transforms applied (Typically via add-ons)
* This configuration will consume all output presuming no S2S is allowed no Splunk destnation will be used

### outputs.conf

```ini
#Because audit trail is protected and we can't transform it we can not use default we must use tcp_routing
[tcpout]
defaultGroup = NoForwarding

[tcpout:nexthop]
server = localhost:9000
sendCookedData = false
```

## props.conf

```ini
[default]
ADD_EXTRA_TIME_FIELDS = none
ANNOTATE_PUNCT = false
SHOULD_LINEMERGE = false
TRANSFORMS-zza-syslog = syslog_canforward, metadata_meta,  metadata_source, metadata_sourcetype, metadata_index, metadata_host, metadata_subsecond, metadata_time, syslog_prefix, syslog_drop_zero
# The following applies for TCP destinations where the IETF frame is required
TRANSFORMS-zzz-syslog = syslog_octal, syslog_octal_append
# Comment out the above and uncomment the following for udp
#TRANSFORMS-zzz-syslog-udp = syslog_octal, syslog_octal_append, syslog_drop_zero

[audittrail]
# We can't transform this source type its protected
TRANSFORMS-zza-syslog =
TRANSFORMS-zzz-syslog =
```

### transforms.conf

```ini
syslog_canforward]
REGEX = ^.(?!audit)
DEST_KEY = _TCP_ROUTING
FORMAT = nexthop

[metadata_meta]
SOURCE_KEY = _meta
REGEX = (?ims)(.*)
FORMAT = ~~~SM~~~$1~~~EM~~~$0 
DEST_KEY = _raw

[metadata_source]
SOURCE_KEY = MetaData:Source
REGEX = ^source::(.*)$
FORMAT = s="$1"] $0
DEST_KEY = _raw

[metadata_sourcetype]
SOURCE_KEY = MetaData:Sourcetype
REGEX = ^sourcetype::(.*)$
FORMAT = st="$1" $0
DEST_KEY = _raw

[metadata_index]
SOURCE_KEY = _MetaData:Index
REGEX = (.*)
FORMAT = i="$1" $0
DEST_KEY = _raw

[metadata_host]
SOURCE_KEY = MetaData:Host
REGEX = ^host::(.*)$
FORMAT = " h="$1" $0
DEST_KEY = _raw

[syslog_prefix]
SOURCE_KEY = _time
REGEX = (.*)
FORMAT = <1>1 - - SPLUNK - COOKED [fields@274489 $0
DEST_KEY = _raw

[metadata_time]
SOURCE_KEY = _time
REGEX = (.*)
FORMAT =  t="$1$0
DEST_KEY = _raw

[metadata_subsecond]
SOURCE_KEY = _meta
REGEX = \_subsecond\:\:(\.\d+)
FORMAT = $1 $0
DEST_KEY = _raw

[syslog_octal]
INGEST_EVAL= mlen=length(_raw)+1

[syslog_octal_append]
INGEST_EVAL = _raw=mlen + " " + _raw

[syslog_drop_zero]
INGEST_EVAL = queue=if(mlen<10,"nullQueue",queue)
```