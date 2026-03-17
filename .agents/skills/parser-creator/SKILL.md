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

1. `cef` - for CEF-formatted messages.
2. `sc4s-syslog-pgm` - matches by program value (`PROGRAM` in RFC3164, `APP-NAME` in RFC5424).
3. `sc4s-syslog-sdata` - matches by structured data (often a Private Enterprise Number, PEN). If PEN is present, prefer this topic.
4. `sc4s-syslog` - general filter for RFC3164/RFC5424, usually based on message content.
5. `sc4s-network-source` - matches by destination port. Use this only when other topics are not viable. Because this requires sending logs to a new port, ask the user for permission first. If the user refuses, stop and explain why parser creation cannot continue.

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