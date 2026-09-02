# SC4S Parser Creation Guide

## Parser structure

A SC4S parser consists of two blocks: a `block parser` (the logic) and an `application` (the filter that routes matching logs to it).

```
block parser app-<type>-<vendor>_<product>() {
    channel {
        <optional: parser stage>
        rewrite {
            r_set_splunk_dest_default(
                index('<index>')
                sourcetype('<vendor>:<product>')
                vendor("<vendor>")
                product("<product>")
                template('<template>')
            );
        };
        <optional: conditional rewrite branches>
    };
};

application app-<type>-<vendor>_<product>[<topic>] {
    filter {
        <filter expression>;
    };
    parser { app-<type>-<vendor>_<product>(); };
};
```

## Filename convention

`app-<type>-<vendor>_<product>.conf`

Use the SC4S parser type appropriate to the format, such as `syslog`, `cef`, or `netsource`. Preserve `<filename>` exactly, including its `.conf` suffix, after selecting it.

## Step 1 — Identify syslog format

- **RFC3164:** `<PRI>TIMESTAMP HOSTNAME PROGRAM: MESSAGE`
- **RFC5424:** `<PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID SDATA MESSAGE`
- **CEF:** `<PRI>TIMESTAMP HOSTNAME CEF:0|Vendor|Product|Version|SigID|Name|Severity|Extensions`

If the format is none of the above, tell the operator it is unsupported and stop.

## Step 2 — Choose the application topic (filter type)

Pick the most specific topic available:

### 1. `cef` — CEF-formatted messages
```
application app-cef-<vendor>_<product>[cef] {
    filter {
        match("<Vendor>" value(".metadata.cef.device_vendor"))
        and match("<Product>" value(".metadata.cef.device_product"));
    };
    parser { app-cef-<vendor>_<product>(); };
};
```

### 2. `sc4s-syslog-pgm` — match by PROGRAM / APP-NAME field (preferred when program is unique)
```
application app-syslog-<vendor>_<product>[sc4s-syslog-pgm] {
    filter {
        program('<program_name>' type(string) flags(prefix));
    };
    parser { app-syslog-<vendor>_<product>(); };
};
```

### 3. `sc4s-syslog-sdata` — match by structured data / PEN (prefer when RFC5424 SDATA is present)
```
application app-syslog-<vendor>_<product>[sc4s-syslog-sdata] {
    filter {
        match('<PEN_or_SDATA_pattern>' value("SDATA"));
    };
    parser { app-syslog-<vendor>_<product>(); };
};
```

### 4. `sc4s-syslog` — general RFC3164/RFC5424 match by message content (fallback)
```
application app-syslog-<vendor>_<product>[sc4s-syslog] {
    filter {
        program('^<regex>$')
        and message('<distinctive_string>' type(string) flags(prefix));
    };
    parser { app-syslog-<vendor>_<product>(); };
};
```

### 5. `sc4s-network-source` — match by source IP/port (last resort — requires operator to route traffic to a new port)
Ask operator permission before using this topic. If they refuse, stop.

## Step 3 — Write the block parser

### Rewrite functions

**`r_set_splunk_dest_default`** — sets all base Splunk metadata. Call this exactly once as the first rewrite in every parser. Always include `index`, `sourcetype`, `vendor`, `product`. Optionally include `source` and `template`.

**`r_set_splunk_dest_update_v2`** — conditionally overrides specific fields already set by the default. Use only inside `if/elif` branches.

### Choose the final event format and namespaces

Choose how the event should appear in Splunk before choosing parser prefixes. A parser can extract fields correctly and still produce an unwanted event if its namespaces and template do not agree.

| Goal | Template | Extraction namespace | Result in Splunk |
|------|----------|----------------------|------------------|
| Preserve the message body; use parsed values only inside SC4S | `t_msg_only` or another raw-message template | `.tmp.*` | Original message body; temporary values are not sent |
| Replace the body with normalized key/value text | `t_kv_values` | `.values.*` | WELF-formatted key/value event |
| Replace the body with JSON | `t_json_values` | `.values.*` | JSON event |
| Include parsed values and the original message as a field | `t_kv_values_msg` or `t_json_values_msg` | `.values.*` | WELF or JSON event containing a `message` field; the body is still transformed |
| Preserve the message body and send indexed fields through Splunk HEC | A raw-message template such as `t_msg_only` | `fields.*` | Original message body plus indexed HEC fields |

Apply these namespace rules:

- Use `.tmp.*` for intermediate fragments, discarded prefixes, and raw tails that must not appear in the event.
- Use `.values.*` only for fields intentionally serialized by a values template.
- Use `fields.*` only when indexed HEC fields are required. This is destination-specific and is not a Splunk search-time field definition.
- Never capture an unparsed tail such as `key="value" key2="value with spaces"` into `.values.*` when using `t_kv_values` or `t_json_values`. The serializer will emit the whole tail as one escaped value alongside any parsed fields.

### Parser methods

**`kv-parser`** — use when the selected input contains key/value pairs or RFC5424 SDATA blocks:
```
parser {
    kv-parser(
        prefix(".values.")
        template("${MESSAGE}")
    );
};
```

When only part of a message contains key/value data, set `template()` to a temporary field containing only that portion. Keep the temporary value in `.tmp.*`; do not also emit it as a `.values.*` field.

**`csv-parser`** — use when logs are consistently delimited with stable column order:
```
parser {
    csv-parser(
        columns("col1","col2","col3")
        prefix(".values.")
        delimiters(',')
        quote-pairs('""')
        flags(escape-double-char)
    );
};
```

**`regexp-parser`** — use when logs are structured but not key/value or delimited:
```
parser {
    regexp-parser(
        template("${MESSAGE}")
        patterns("^(?<field1>\\d+) (?<field2>[^ ]+) (?<field3>.*)")
        prefix(".tmp.")
    );
};
```

Syslog-ng string quoting changes how regular expressions are written:

```conf
# Single-quoted string: write literal double quotes and regex backslashes directly.
patterns('rc="(?<rc>[^"]*)"')

# Double-quoted string: escape double quotes and regex backslashes.
patterns("rc=\"(?<rc>[^\"]*)\"")
```

Prefer single-quoted strings for regular expressions when the pattern does not contain an apostrophe. For example, write `\d` in a single-quoted pattern and `\\d` in a double-quoted pattern.

The examples above are `.conf` content. MCP or JSON transport may display additional backslashes when serializing that content; do not copy those transport escapes back into the parser.

**Conditional branches** — combine methods for logs with multiple variants:
```
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
    ...
} else { };
```

## Complete minimal example (RFC5424, SDATA-based)

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

## Authoring checklist

- Confirm whether the event body must remain unchanged or may become WELF or JSON.
- Confirm every requested field and its exact expected value for each sample.
- Keep intermediate fragments and unparsed tails in `.tmp.*`.
- Ensure the selected output template consumes the namespace used for final fields.
- Inspect literal quotes and backslashes in the final `.conf`, not its JSON-serialized representation.
- For the full template list, inspect `t_templates.conf` in the SC4S package.

## Deployment path

- Deploy to a running SC4S instance: `/opt/sc4s/local/config/app_parsers/<filename>`
- Restart SC4S after deploying: `sudo systemctl restart sc4s` or `docker restart sc4s`
