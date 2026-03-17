---
name: parser-creator
description: Creates SC4S syslog-ng parsers. Use when the user wants to create a new parser, add support for a new log source or vendor, or says "create parser", "add parser", "new log source", or "new vendor support".
---

# Parser Creator

You can use only command to run the unit tests `poetry run pytest test-name -v -s --tb=short -n=0`

## Goal

Create a new SC4S parser and test coverage for a vendor/product pair in both:

- main package (`package/etc/conf.d/conflib`)
- lite package (`package/lite/etc/addons`)

## Prerequites

Collect this information from the user before you start:

1. `vendor`: vendor name (lowercase, for example `acme`)
2. `product`: product name (lowercase, for example `firewall`)
3. `sourcetype`: target Splunk sourcetype using `vendor:product` (for example `acme:firewall`)
4. `index`: target Splunk index (for example `netfw`)
5. `sample logs`: one or more raw syslog messages

If any item is missing, ask for it before proceeding. 

## Workflow

### Step 1 - Identify message format

Examine the sample logs and identify the Syslog format.

1. RFC3164: `<PRI>TIMESTAMP HOSTNAME PROGRAM: MESSAGE`
2. RFC5424: `<PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID SDATA MESSAGE`
3. CEF: `<PRI>TIMESTAMP HOSTNAME CEF:0|<Device Vendor>|<Device Product>|<Device Version>|<Signature ID>|<Name>|<Severity>|<Extension fields>`

If logs do not match one of these formats, tell the user the format is currently unsupported and stop.

### Step 2 - Create a parser

Start by creating a filter for the log message. Filter has a following structure:

```
application <filter-name>[<topic>] {
    filter {
        <filter_block>
    };
    parser { <parser-name>(); };
};
```

Filter are grouped into topics. Use one of the following topics:

1. `cef` - for CEF-formatted messages. Example:
```
application app-cef-a10_vthunder[cef] {
    filter{
        match("A10" value(".metadata.cef.device_vendor"))
        and match("vThunder" value(".metadata.cef.device_product"));
    };
    parser { app-cef-a10_vthunder(); };
};
```
2. `sc4s-syslog-pgm` - matches by program value (`PROGRAM` in RFC3164, `APP-NAME` in RFC5424). Example:
```
application app-syslog-alcatel_switch[sc4s-syslog-pgm] {
	filter {
        program('swlogd' type(string) flags(prefix));
    };	
    parser { app-syslog-alcatel_switch(); };
};
```
3. `sc4s-syslog-sdata` - matches by structured data (often a Private Enterprise Number, PEN). If PEN is present, prefer this topic. Example:
```
application app-syslog-f5_bigip_structured[sc4s-syslog-sdata] {
	filter {
        match('^\[F5@12276' value("SDATA"))
        ;
    };	
    parser { app-syslog-f5_bigip_structured(); };
};
```
4. `sc4s-syslog` - general filter for RFC3164/RFC5424, usually based on message content. Example:
```
application app-syslog-arista_eos[sc4s-syslog] {
	filter {
        program('^[A-Z]\S+$')
        and message('%' type(string) flags(prefix));
    };	

    parser { app-syslog-arista_eos(); };
};
```
5. `sc4s-network-source` - matches by destination port. Use this only when other topics are not viable. Because this requires sending logs to a new port, ask the user for permission first. If the user refuses, stop and explain why parser creation cannot continue. Example:
```
application app-netsource-brocade_syslog[sc4s-network-source] {
	filter {
        not filter(f_is_source_identified)
        and (
            (
                    match("brocade", value('.netsource.sc4s_vendor'), type(string)) 
                    and match("syslog", value('.netsource.sc4s_product'), type(string)) 
                )
                or (tags("ns_vendor:brocade") and tags("ns_product:syslog"))
            or tags(".source.s_BROCADE")
            or "${.netsource.sc4s_vendor_product}" eq "brocade_syslog"
            )


    };	
    parser { app-netsource-brocade_syslog(); };
};
```

Next create `block parser`:

```
block parser <parser-name>() {
    <parsers and filters blocks>
    <rewrite block>
};
```

If structured data or repeated key/value data exists, include a parser stage (`kv-parser`, `csv-parser`, or `regexp-parser`) before rewrite. Only skip parsing when the message is truly unstructured; if so, explicitly state this in the final response.

There are two rewrite functions. Choose the correct one:

1. `r_set_splunk_dest_default` — sets **all** base Splunk metadata. Every parser MUST call this exactly once as its first rewrite. Always include `index`, `sourcetype`, `vendor`, and `product`. Optionally include `source` and `template`.
2. `r_set_splunk_dest_update_v2` — **conditionally overrides** specific fields that were already set by `r_set_splunk_dest_default`. Use this ONLY in `if/elif` branches to change a subset of fields (e.g. sourcetype, index) based on message content. Never use it as the first or only rewrite.

`r_set_splunk_dest_default` example (required in every parser):

```
rewrite {
    r_set_splunk_dest_default(
        index('netops')
        sourcetype('alcatel:switch')
        vendor("alcatel")
        product("switch")
        template('t_hdr_msg')
    );
};
```

`r_set_splunk_dest_update_v2` example (optional, only after default is set):

```
rewrite {
    r_set_splunk_dest_update_v2(
            sourcetype('citrix:netscaler:appfw') condition(message(':(\s+\S+)?\s+APPFW(\s+\S+){3}\s+:'))
    );
};
```

To choose correct template refer to the definitions in file: `t_templates.conf`.

Parser method selection:

Use `kv-parser` when logs contain key/value pairs (`key=value`, quoted values, RFC5424 SDATA blocks).
   - For RFC5424 SDATA, prefer `template("${SDATA}")`.
   - Use a scoped prefix like `.values.sdata.`.

Example:

```
block parser app-syslog-vendor_product() {
    channel {
        parser {
            kv-parser(prefix(".values.") template("$(template t_hdr_msg)"));
        };
        # Optional: validate parsing succeeded
        filter {
            "${.values.some_required_field}" ne ""
        };
        rewrite {
            r_set_splunk_dest_default(
                index('netfw')
                sourcetype('vendor:product')
                vendor("vendor")
                product("product")
                template('t_kv_values')
            );
        };
    };
};
```

Use `csv-parser` when logs are consistently delimited and have stable column order.

Example:

```
parser {
    csv-parser(
        columns("col1","col2","col3","col4")
        prefix(".values.")
        delimiters(',')
        quote-pairs('""')
        flags(escape-double-char)
    );
};
```

Use `regexp-parser` when logs are structured but not key/value or delimited.
Combine methods when logs have multiple variants.

Example:

```
parser {
    regexp-parser(
        template("${MESSAGE}")
        patterns("^(?<field1>\\d+) (?<field2>[^ ]+) (?<field3>.*)")
        prefix(".parsed.")
    );
};
```

You can combine all methods and use conditional branches to parse different message variants:

```
block parser app-syslog-vendor_product() {
    channel {
        rewrite {
            r_set_splunk_dest_default(
                index("netops")
                sourcetype('vendor:log')
                vendor("vendor")
                product('product')
                template('t_msg_only')
            );
        };

        if (message(',TRAFFIC,' type(string) flags(substring))) {
            parser { csv-parser(columns(...) prefix(".values.") delimiters(',')); };
            rewrite {
                r_set_splunk_dest_update_v2(
                    index('netfw')
                    class('traffic')
                    sourcetype('vendor:traffic')
                );
            };
        } elif (message(',SYSTEM,' type(string) flags(substring))) {
            parser { csv-parser(columns(...) prefix(".values.") delimiters(',')); };
            rewrite {
                r_set_splunk_dest_update_v2(
                    index('netops')
                    class('system')
                    sourcetype('vendor:system')
                );
            };
        } else { };
    };
};
```

### Step 4 - Create unit test

Create a unit test for the new parser. Testing instructions: [testing-parsers](./references/testing-parsers.md).

### Step 5 - Run parser tests

Run the new test using `poetry run pytest test-name -v -s --tb=short -n=0` command and verify the parser works correctly.

## Workflow Example

User input:

```
vendor: thinkst
product: canary
sourcetype: thinkst:canary
index: netfw
logs:
  <130>1 2025-04-30T12:09:54.681299+00:00 mycompany-com ThinkstCanary 3545385 newincident
  [BasicIncidentDetails@51136 Description="Web Bug Canarytoken triggered"
  Timestamp="2025-04-30 12:07:53 (UTC)" Reminder="q" Token="d7a7phdpurh2vs8gs1jbniyhb"
  SourceIP="192.168.1.97" IncidentHash="40a96cf3ba4596a81f18990143916b3c" eventid="17000"]

  [AdditionalIncidentDetails@51136
  Abbr="SAST" Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
  Accept-Encoding="gzip, deflate" Accept-Language="en-GB,en-US;q=0.9,en;q=0.8,ro;q=0.7"
  BackgroundContext="You have had 214 incidents from 192.168.1.97 previously."
  Browser="Chrome" Cache-Control="max-age=0" City="Cape Town" Connection="keep-alive"
  ContinentCode="AF" Country="South Africa" CountryCode="ZA" CountryCode3="ZAF" CurrencyCode="ZAR"
  Date="2025-04-30" DstPort="80" Enabled="1" Host="123456789abe[.\]o3n[.\]io" HostDomain=""
  Hostname="" Id="Africa/Johannesburg" Installed="1" Ip="192.168.1.97" IsBogon="False"
  IsProxy="False" IsTor="False" IsV4Mapped="False" IsV6="False" IsVpn="False" Language="en-GB"
  LanguageCode="zu" Latitude="-33.925552" Longitude="18.422857"
  Mimetypes="Portable Document Format;pdf;application/pdf|||Portable Document Format;pdf;text/pdf|||"
  Name="South Africa Standard Time" Offset="+02:00" Os="Macintosh" Platform="MacIntel"
  Region="Western Cape" RegionCode="WC" SrcPort="54290" Time="14:07:53.846452"
  Upgrade-Insecure-Requests="1"
  User-Agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
  Valid="True" Vendor="Google Inc." Version="135.0.0.0"]
  A Web Bug Canarytoken was triggered by '192.168.1.97'.


  <130>1 2025-04-30T12:54:52.796337+00:00 mycompany-com ThinkstCanary 3557764 newincident
  [BasicIncidentDetails@51136 Description="DNS Canarytoken triggered"
  Timestamp="2025-04-30 12:52:49 (UTC)" Reminder="q" Token="vv4x12n26ivmcgyd33pkb3drr"
  SourceIP="1.1.1.1" IncidentHash="adaa8486af78cc450417b027e2821a22" eventid="16000"]

  [AdditionalIncidentDetails@51136 BackgroundContext="This alert is the first from 1.1.1.1."
  DstPort="53" Hostname="VV4x12N26IvMcgyd33pKB3DRr[.\]123456789abe[.\]o3N[.\]Io" SrcPort="48908"]
  A DNS Canarytoken was triggered by a DNS query from the source IP 1.1.1.1.
  Please note that the source IP refers to a DNS resolver, rather than the host that triggered the token.
```

Created parser:

```
block parser app-syslog-thinkst_canary() {
    channel {
        parser {
            kv-parser(
                prefix(".values.sdata.")
                template("${SDATA}")
            );
        };
        rewrite {
            r_set_splunk_dest_default(
                index('netfw')
                sourcetype('thinkst:canary')
                vendor("thinkst")
                product("canary")
                template('t_5424_hdr_sdata_compact')
            );
        };
    };
};

application app-syslog-thinkst_canary[sc4s-syslog-sdata] {
    filter {
        filter(f_is_rfc5424)
        and program("ThinkstCanary")
        and match('@51136' value("SDATA"));
    };
    parser { app-syslog-thinkst_canary(); };
};
```

Created unit test:

```
# Copyright 2026 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import pytest

from jinja2 import Environment, select_autoescape

from .sendmessage import sendsingle
from .splunkutils import splunk_single
from .timeutils import time_operations

env = Environment(autoescape=select_autoescape(default_for_string=False))


@pytest.mark.addons("thinkst")
@pytest.mark.parametrize(
    "procid,basic_details,additional_details,incident_message",
    [
        (
            "3545385",
            '[BasicIncidentDetails@51136 Description="Web Bug Canarytoken triggered" Timestamp="2025-04-30 12:07:53 (UTC)" Reminder="q" Token="d7a7phdpurh2vs8gs1jbniyhb" SourceIP="192.168.1.97" IncidentHash="40a96cf3ba4596a81f18990143916b3c" eventid="17000"]',
            '[AdditionalIncidentDetails@51136 Abbr="SAST" Accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" Accept-Encoding="gzip, deflate" Accept-Language="en-GB,en-US;q=0.9,en;q=0.8,ro;q=0.7" BackgroundContext="You have had 214 incidents from 192.168.1.97 previously." Browser="Chrome" Cache-Control="max-age=0" City="Cape Town" Connection="keep-alive" ContinentCode="AF" Country="South Africa" CountryCode="ZA" CountryCode3="ZAF" CurrencyCode="ZAR" Date="2025-04-30" DstPort="80" Enabled="1" Host="123456789abe[.\\]o3n[.\\]io" HostDomain="" Hostname="" Id="Africa/Johannesburg" Installed="1" Ip="192.168.1.97" IsBogon="False" IsProxy="False" IsTor="False" IsV4Mapped="False" IsV6="False" IsVpn="False" Language="en-GB" LanguageCode="zu" Latitude="-33.925552" Longitude="18.422857" Mimetypes="Portable Document Format;pdf;application/pdf|||Portable Document Format;pdf;text/pdf|||" Name="South Africa Standard Time" Offset="+02:00" Os="Macintosh" Platform="MacIntel" Region="Western Cape" RegionCode="WC" SrcPort="54290" Time="14:07:53.846452" Upgrade-Insecure-Requests="1" User-Agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36" Valid="True" Vendor="Google Inc." Version="135.0.0.0"]',
            "A Web Bug Canarytoken was triggered by '192.168.1.97'.",
        ),
        (
            "3557764",
            '[BasicIncidentDetails@51136 Description="DNS Canarytoken triggered" Timestamp="2025-04-30 12:52:49 (UTC)" Reminder="q" Token="vv4x12n26ivmcgyd33pkb3drr" SourceIP="1.1.1.1" IncidentHash="adaa8486af78cc450417b027e2821a22" eventid="16000"]',
            '[AdditionalIncidentDetails@51136 BackgroundContext="This alert is the first from 1.1.1.1." DstPort="53" Hostname="VV4x12N26IvMcgyd33pKB3DRr[.\\]123456789abe[.\\]o3N[.\\]Io" SrcPort="48908"]',
            "A DNS Canarytoken was triggered by a DNS query from the source IP 1.1.1.1. Please note that the source IP refers to a DNS resolver, rather than the host that triggered the token.",
        ),
    ],
)
def test_thinkst_canary(
    record_property,
    get_host_key,
    setup_splunk,
    setup_sc4s,
    procid,
    basic_details,
    additional_details,
    incident_message,
):
    host = get_host_key

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, _, _, _, _, _, epoch = time_operations(dt)

    # Tune time functions
    epoch = epoch[:-3]

    mt = env.from_string(
        "{{ mark }} {{ iso }} {{ host }} ThinkstCanary {{ procid }} newincident {{ basic_details }} {{ additional_details }} {{ incident_message }}\n"
    )
    message = mt.render(
        mark="<130>1",
        iso=iso,
        host=host,
        procid=procid,
        basic_details=basic_details,
        additional_details=additional_details,
        incident_message=incident_message,
    )

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netfw host="{{ host }}" sourcetype="thinkst:canary"'
    )
    search = st.render(epoch=epoch, host=host)

    result_count, _ = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", result_count)
    record_property("message", message)

    assert result_count == 1
```

## Completion Checklist

Before finishing, confirm all items:

- Parser/filter created for main package.
- Parser/filter created for lite package.
- Parser includes field extraction (`kv-parser`, `csv-parser`, and/or `regexp-parser`) when sample logs are parseable.
- Lite vendor metadata exists (`addon_metadata.yaml`) when required.
- `package/lite/etc/config.yaml` updated for new lite vendor addon.
- Unit tests created and passing for the new parser.
- User informed about any constraints (for example, unsupported format or required network-source port changes).
- The parser files have only one `block parser` definition and only one `application` deffinition.