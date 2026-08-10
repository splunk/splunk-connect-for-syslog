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

### Parser methods

**`kv-parser`** — use when logs contain key=value pairs or RFC5424 SDATA blocks:
```
parser {
    kv-parser(
        prefix(".values.sdata.")
        template("${SDATA}")
    );
};
```

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
        prefix(".parsed.")
    );
};
```

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

## Common templates

| Template | Use |
|----------|-----|
| `t_msg_only` | Pass message body only |
| `t_hdr_msg` | Syslog header + message |
| `t_5424_hdr_sdata_compact` | RFC5424 header + compact SDATA |
| `t_kv_values` | Key/value extracted fields |

For the full list, see `t_templates.conf` in the SC4S package.

## Deployment path

- Deploy to a running SC4S instance: `/opt/sc4s/local/config/app_parsers/<filename>`
- Restart SC4S after deploying: `sudo systemctl restart sc4s` or `docker restart sc4s`
