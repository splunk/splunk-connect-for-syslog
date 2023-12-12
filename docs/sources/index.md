# Introduction

When using Splunk Connect for Syslog to onboard a data source, the syslog-ng "app-parser" performs the operations that are traditionally performed at index-time by the corresponding Technical Add-on installed there. These index-time operations include linebreaking, source/sourcetype setting and timestamping. For this reason, if a data source is exclusively onboarded using SC4S then you will not need to install its corresponding Add-On on the indexers. You must, however, install the Add-on on the search head(s) for the user communities interested in this data source.

SC4S is designed to process "syslog" referring to IETF RFC standards 5424, legacy BSD syslog, RFC3164 (Not a standard document), and many "almost" syslog formats.

When possible data sources are identified and processed based on characteristics of the event that make them unique as compared to other events for example. Cisco devices using IOS will include " : %" followed by a string. While Arista EOS devices will use a valid RFC3164 header with a value in the "PROGRAM" position with "%" as the first char in the "MESSAGE" portion. This allows two similar event structures to be processed correctly.

When identification by message content alone is not possible for example the "sshd" program field is commonly used across vendors additional "hint" or guidance configuration allows SC4S to better classify events. The hints can be applied by
definition of a specific port which will be used as a property of the event or by configuration of a host name/ip pattern. For example "VMWARE VSPHERE" products have a number of "PROGRAM" fields which can be used to identify vmware specific events in the syslog stream and these can be properly sourcetyped automatically however because "sshd" is not unique it will be treated as generic "os:nix" events until further configuration is applied. The administrator can take one of two actions to refine the processing for vmware

* Define a specific port for vmware and reconfigure sources to use the defined port "SC4S_LISTEN_VMWARE_VSPHERE_TCP=9000". Any events arriving on port 9000 will now have a metadata field attached ".netsource.sc4s_vendor_product=VMWARE_VSPHERE"
* Define a "app-parser" to apply the metadata field by using a syslog-ng filter to apply the metadata field.

## Supporting previously unknown sources

Many log sources can be supported using one of the flexible options available without specific code known as app-parsers.

New supported sources are added regularly. Please submit an [issue](https://github.com/splunk/splunk-connect-for-syslog/issues) with a description of the vend/product. Configuration information an a compressed pcap (.zip) from a non-production environment to request support for a new source.

Many sources can be self supported. While we encourage sharing new sources via the github project to promote consistency and develop best-practices there is no requirement to engage in the community.

* Sources that are *compliant* with RFC 5424,RFC 5425, RFC 5426, or RFC 6587 can be onboarded as [simple sources](https://splunk.github.io/splunk-connect-for-syslog/main/sources/base/simple/)
* Sources "compatible" with RFC3164 Note incorrect use of the syslog version, or "creative" formats in the time stamp or other fields may prevent use as [simple sources](https://splunk.github.io/splunk-connect-for-syslog/main/sources/base/simple/)
* Common Event Format [CEF](https://splunk.github.io/splunk-connect-for-syslog/main/sources/base/cef/) Also known as ArcSight format
* Log Extended Format [LEEF](https://splunk.github.io/splunk-connect-for-syslog/main/sources/base/leef/)

### Almost Syslog

Sources sending legacy non conformant 3164 like streams can be assisted by the creation of an "Almost Syslog" Parser. In an such a parser the goal is to process the syslog header allowing other parsers
to correctly parse and handle the event. The following example is take from a currently supported format where the source product used epoch in the time stamp field.

```c
    #Example event
    #<134>1 1563249630.774247467 devicename security_event ids_alerted signature=1:28423:1 
    # In the example note the vendor incorrectly included "1" following PRI defined in RFC5424 as indicating a compliant message
    # The parser must remove the 1 before properly parsing
    # The epoch time is captured by regex
    # The epoch time is converted back into an RFC3306 date and provided to the parser
    block parser syslog_epoch-parser() {    
    channel {
            filter { 
                message('^(\<\d+\>)(?:1(?= ))? ?(\d{10,13}(?:\.\d+)?) (.*)', flags(store-matches));
            };  
            parser {             
                date-parser(
                    format('%s.%f', '%s')
                    template("$2")
                );
            };
            parser {
                syslog-parser(

                    flags(assume-utf8, expect-hostname, guess-timezone)
                    template("$1 $S_ISODATE $3")
                    );
            };
            rewrite(set_rfc3164_epoch);                       
            
    };
    };
    application syslog_epoch[sc4s-almost-syslog] {
        parser { syslog_epoch-parser(); };   
    };
```

## Standard Syslog using message parsing

Syslog data conforming to RFC3164 or complying with RFC standards mentioned above can be processed with an app-parser allowing the use of the default port
rather than requiring custom ports the following example take from a currently supported source uses the value of "program" to identify the source as this program value is
unique. Care must be taken to write filter conditions strictly enough to not conflict with similar sources

```c
block parser alcatel_switch-parser() {    
 channel {
        rewrite {
            r_set_splunk_dest_default(
                index('netops')
                sourcetype('alcatel:switch')
                vendor('alcatel')
                product('switch')
                template('t_hdr_msg')
            );              
        };       
       

   };
};
application alcatel_switch[sc4s-syslog] {
 filter { 
        program('swlogd' type(string) flags(prefix));
    }; 
    parser { alcatel_switch-parser(); };   
};
```

## Standard Syslog vendor product by source

In some cases standard syslog is also generic and can not be disambiguated from other sources by message content alone.
When this happens and only a single source type is desired the "simple" option above is valid but requires managing a port.
The following example allows use of a named port OR the vendor product by source configuration.

```c
block parser dell_poweredge_cmc-parser() {    
 channel {
        
        rewrite {
            r_set_splunk_dest_default(
                index('infraops')
                sourcetype('dell:poweredge:cmc:syslog')
                vendor('dell')
                product('poweredge')
                class('cmc')
            );              
        };       
   };
};
application dell_poweredge_cmc[sc4s-network-source] {
 filter { 
        ("${.netsource.sc4s_vendor_product}" eq "dell_poweredge_cmc"
        or "${SOURCE}" eq "s_DELL_POWEREDGE_CMC")
         and "${fields.sc4s_vendor_product}" eq ""
    };    

    parser { dell_poweredge_cmc-parser(); };   
};
```

### Filtering events from output

In some cases specific events may be considered "noise" and functionality must be implemented to prevent forwarding of these events to Splunk
In version 2.0.0 of SC4S a new feature was implemented to improve the ease of use and efficiency of this progress.

The following example will "null_queue" or drop cisco IOS device events at the debug level. Note Cisco does not use the PRI to indicate DEBUG a message filter is required.

```c
block parser cisco_ios_debug-postfilter() {
    channel {
        #In this case the outcome is drop the event other logic such as adding indexed fields or editing the message is possible
        rewrite(r_set_dest_splunk_null_queue);
   };
};
application cisco_ios_debug-postfilter[sc4s-postfilter] {
 filter {
        "${fields.sc4s_vendor}" eq "cisco" and
        "${fields.sc4s_product}" eq "ios"
        #Note regex reads as
        # start from first position
        # Any atleast 1 char that is not a `-`
        # constant '-7-'
        and message('^%[^\-]+-7-');
    };
    parser { cisco_ios_debug-postfilter(); };
};
```

## Another example to drop events based on "src" and "action" values in  message
```c
#filename: /opt/sc4s/local/config/app_parsers/rewriters/app-dest-rewrite-checkpoint_drop

block parser app-dest-rewrite-checkpoint_drop-d_fmt_hec_default() {    
    channel {
        rewrite(r_set_dest_splunk_null_queue);
    };
};

application app-dest-rewrite-checkpoint_drop-d_fmt_hec_default[sc4s-lp-dest-format-d_hec_fmt] {
    filter {
        match('checkpoint' value('fields.sc4s_vendor') type(string))
        and match('syslog' value('fields.sc4s_product') type(string))

        and match('Drop' value('.SDATA.sc4s@2620.action') type(string))
        and match('12.' value('.SDATA.sc4s@2620.src') type(string) flags(prefix) );

    };    
    parser { app-dest-rewrite-checkpoint_drop-d_fmt_hec_default(); };   
};
```

## The SC4S "fallback" sourcetype

If SC4S receives an event on port 514 which has no soup filter, that event will be given a "fallback" sourcetype. If you see events in Splunk with the fallback sourcetype, then you should figure out what source the events are from and determine why these events are not being sourcetyped correctly. The most common reason for events categorized as "fallback" is the lack of a SC4S filter for that source, and in some cases a misconfigured relay which alters the integrity of the message format. In most cases this means a new SC4S filter must be developed. In this situation you can either build a filter or file an issue with the community to request help.

The "fallback" sourcetype is formatted in JSON to allow the administrator to see the constituent syslog-ng "macros" (fields) that have been automatically parsed by the syslog-ng server An RFC3164 (legacy BSD syslog) "on the wire" raw message is usually (but unfortunately not always) comprised of the following syslog-ng macros, in this order and spacing:

```
<$PRI> $HOST $LEGACY_MSGHDR$MESSAGE
```

These fields can be very useful in building a new filter for that sourcetype.  In addition, the indexed field `sc4s_syslog_format` is helpful in determining if the incoming message is standard RFC3164. A value of anything other than `rfc3164` or `rfc5424_strict` indicates a vendor perturbation of standard syslog, which will warrant more careful examination when building a filter.

## Splunk Connect for Syslog and Splunk metadata

A key aspect of SC4S is to properly set Splunk metadata prior to the data arriving in Splunk (and before any TA processing takes place.  The filters will apply the proper index, source, sourcetype, host, and timestamp metadata automatically by individual data source.  Proper values for this metadata (including a recommended index) are included with all "out-of-the-box" log paths included with SC4S and are chosen to properly interface with the corresponding TA in Splunk.  The administrator will need to ensure all recommended indexes be created to accept this data if the defaults are not changed.

It is understood that default values will need to be changed in many installations.  Each source documented in this section has a table entitled "Sourcetype and Index Configuration", which highlights the default index and sourcetype for each source.  See the section "SC4S metadata configuration" in the "Configuration" page for more information on how to override the default values in this table.

## Unique listening ports

SC4S supports unique listening ports for each source technology/log path (e.g. Cisco ASA), which is useful when the device is
sending data on a port different from the typical default syslog port (UDP port 514).  In some cases, when the source device emits data that
is not able to be distinguished from other device types, a unique port is sometimes required.  The specific environment variables used for
setting "unique ports" are outlined in each source document in this section.

__Using the default ports as unique listening ports is discouraged since it can lead to unintended consequences. There were cases of customers using port 514 as the unique listening port dedicated for a particular vendor and then sending other events to the same port, which caused some of those events to be misclassified.__

In most cases only one "unique port" is needed for each source.  However, SC4S also supports multiple network listening ports per source,
which can be useful for a narrow set of compliance use cases. When configuring a source port variable to enable multiple ports, use a
comma-separated list with no spaces (e.g. `SC4S_LISTEN_CISCO_ASA_UDP_PORT=5005,6005`).

### Filtering by an extra product description
Due to the fact that unique listening port feature differentiate vendor and product based on the first two underscore characters ('_'), it is possible 
to filter events by an extra string added to the product.
For example in case of having several devices of the same type sending logs over different ports it is possible to route it to different indexes based only on port value while retaining proper
vendor and product fields.
In general, it follows convention:
```
SC4S_LISTEN_{VENDOR}_{PRODUCT}_{PROTOCOL}_PORT={PORT VALUE 1},{PORT VALUE 2}...
```
But for special use cases it can be extended to:
```
SC4S_LISTEN_{VENDOR}_{PRODUCT}_{ADDITIONAL_STRING}_{PROTOCOL}_PORT={PORT VALUE},{PORT VALUE 2}...
```
This feature removes the need for complex pre/post filters.

Example:
```
SC4S_LISTEN_EAMPLEVENDOR_EXAMPLEPRODUCT_GROUP01-001_UDP_PORT=18514

sets:
vendor = < example vendor >
product = < example product >
tag = .source.s_EAMPLEVENDOR_EXAMPLEPRODUCT_GROUP01-001
```
```
SC4S_LISTEN_EAMPLEVENDOR_EXAMPLEPRODUCT_GROUP01-002_UDP_PORT=28514

sets:
vendor = < example vendor >
product = < example product >
tag = .source.s_EAMPLEVENDOR_EXAMPLEPRODUCT_GROUP01-002
```