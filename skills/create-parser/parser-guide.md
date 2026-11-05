# SC4S Parser Creation Guide

## Parser structure

An ordinary destination-setting SC4S parser consists of a `block parser` containing the processing logic and an `application` that routes matching events to it:

```conf
block parser app-<type>-<vendor>_<product>() {
    channel {
        <optional: preprocessing rewrites>
        <optional: one or more parser stages>
        <optional: validation filter>
        rewrite {
            r_set_splunk_dest_default(
                index('<index>')
                sourcetype('<vendor>:<product>')
                vendor('<vendor>')
                product('<product>')
                template('<template>')
            );
        };
        <optional: conditional parser or rewrite branches>
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

Use `app-<type>-<vendor>_<product>.conf`, where the single vendor/product boundary is unambiguous. Select the type used by the closest matching shipped parser, such as `syslog`, `cef`, `leef`, `json`, `netsource`, or `almost-syslog`. Preserve `<filename>` exactly, including its `.conf` suffix, after selecting it.

## Step 1 — Identify framing and payload format

Identify the syslog framing separately from the payload format:

- **RFC3164:** `<PRI>TIMESTAMP HOSTNAME PROGRAM: MESSAGE`
- **RFC5424:** `<PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID SDATA MESSAGE`
- **CEF:** a payload beginning with `CEF:0|Vendor|Product|Version|SigID|Name|Severity|Extensions`. CEF can appear after an RFC header, in `PROGRAM`, in `MESSAGE`, or directly after `<PRI>` without timestamp and hostname.
- **LEEF:** a payload beginning with `LEEF:1.0|...` or `LEEF:2.0|...`, usually transported through syslog and processed by SC4S's base LEEF path.
- **JSON:** a JSON payload handled by the base JSON parser before vendor applications on the `json` topic.
- **Almost syslog:** a non-conformant RFC3164/RFC5424-like header that must be normalized and reparsed before normal application routing.

Do not reject an unfamiliar sample until checking the current parser-creation documentation and the closest shipped parsers. If no supported framing, payload path, or safe normalization applies, report the unsupported format and stop.

## Step 2 — Choose the application topic and filter

Use a specialized payload topic when SC4S already parses the payload into metadata. 

### `cef` — parsed CEF metadata

```conf
application app-cef-<vendor>_<product>[cef] {
    filter {
        match('<Vendor>' value('.metadata.cef.device_vendor') type(string))
        and match('<Product>' value('.metadata.cef.device_product') type(string));
    };
    parser { app-cef-<vendor>_<product>(); };
};
```

### `leef` — parsed LEEF metadata

```conf
application app-leef-<vendor>_<product>[leef] {
    filter {
        match('<Vendor>' value('.metadata.leef.vendor') type(string))
        and match('<Product>' value('.metadata.leef.product') type(string));
    };
    parser { app-leef-<vendor>_<product>(); };
};
```

### `json` — parsed JSON values

Use stable, product-specific keys already produced by the base JSON parser. Do not assume every JSON source has vendor and product fields.

```conf
application app-json-<vendor>_<product>[json] {
    filter {
        match('<expected-value>' value('.values.<stable-key>') type(string));
    };
    parser { app-json-<vendor>_<product>(); };
};
```

### `sc4s-syslog-sdata` — structured data or PEN

This topic has precedence over the program topic whenever enterprise SDATA is present.

```conf
application app-syslog-<vendor>_<product>[sc4s-syslog-sdata] {
    filter {
        match('^\[<SD-ID-or-PEN>' value('SDATA'));
    };
    parser { app-syslog-<vendor>_<product>(); };
};
```

### `sc4s-syslog-pgm` — unique PROGRAM or APP-NAME

Use this only when the event is eligible for the PGM stage and the program value is a stable product discriminator.

```conf
application app-syslog-<vendor>_<product>[sc4s-syslog-pgm] {
    filter {
        program('<program-name>' type(string));
    };
    parser { app-syslog-<vendor>_<product>(); };
};
```

Add `flags(prefix)` only when a prefix match is intentional and cannot collide with another source.

### `sc4s-syslog` — message-content fallback

```conf
application app-syslog-<vendor>_<product>[sc4s-syslog] {
    filter {
        program('^<anchored-regex>$')
        and message('<distinctive-prefix>' type(string) flags(prefix));
    };
    parser { app-syslog-<vendor>_<product>(); };
};
```

### `sc4s-network-source` — pre-enriched source identity

Use this when content alone cannot distinguish the source. The identity can come from a dedicated destination listener or existing hostname/IP/vendor-product-by-source enrichment.

```conf
application app-netsource-<vendor>_<product>[sc4s-network-source] {
    filter {
        not filter(f_is_source_identified)
        and (
            (
                match('<vendor>' value('.netsource.sc4s_vendor') type(string))
                and match('<product>' value('.netsource.sc4s_product') type(string))
            )
            or (tags('ns_vendor:<vendor>') and tags('ns_product:<product>'))
            or tags('.source.s_<VENDOR_PRODUCT>')
            or "${.netsource.sc4s_vendor_product}" eq '<vendor>_<product>'
        );
    };
    parser { app-netsource-<vendor>_<product>(); };
};
```

Inspect existing enrichment before proposing a new listener. If a new destination port is the only reliable discriminator, explain the SC4S configuration change and ask the operator before using it.

### `sc4s-almost-syslog` — normalize a malformed header

Use a narrowly matching parser that reconstructs a valid syslog line with `regexp-parser`, optional `date-parser`, and `syslog-parser`. The application can rely on parser success when the block itself performs the identifying match.

```conf
application app-almost-syslog-<vendor>_<product>[sc4s-almost-syslog] {
    parser { app-almost-syslog-<vendor>_<product>(); };
};
```

### `sc4s-postfilter` — mutate or drop an already identified event

Use a postfilter only when the requested behavior applies after source identification, such as dropping a noisy event class. Filter on the established `fields.sc4s_vendor` and `fields.sc4s_product` values as well as the event-specific condition.

## Filter semantics

Choose the narrowest stable discriminator and use the field-aware function that matches it:

- `program()` matches only RFC3164 `PROGRAM` or RFC5424 `APP-NAME`.
- `message()` matches only `MESSAGE`.
- `match(pattern)` matches the message header plus message; use `value()` or `template()` to target another field such as `SDATA`, `MSGHDR`, or a parsed value.
- `host()` matches `HOST`.
- `"${MACRO}" eq "value"` and `ne` perform equality comparisons. Backtick expansion is for SC4S environment variables, not message macros.
- `tags()` matches source, vendor/product, or wire-format tags and is preferable to reparsing content when a stable tag already exists.

## Step 3 — Write the block parser

### Splunk destination rewrites

**`r_set_splunk_dest_default`** — sets all base Splunk metadata. Include `index`, `sourcetype`, `vendor`, and `product` for ordinary source parsers. Add `source`, `class`, or `template` when required by the target Splunk integration.

**`r_set_splunk_dest_update_v2`** overrides selected metadata after a default has been established. Use it either inside an `if/elif` branch or with its `condition()` argument:

### Other rewrite operations

- `set()` copies or assigns a value, including to `HOST`, `PROGRAM`, or `MESSAGE`.
- `subst()` performs a scoped string or regular-expression substitution.
- `unset()` removes a field such as an invalid `PROGRAM` or `PID`.
- `map-value-pairs()` remaps groups of name-value pairs between namespaces.
- `rewrite(r_set_dest_splunk_null_queue)` drops an event in a postfilter.

### Choose the final event format and namespaces

Ask what must be preserved instead of treating every raw-message template as equivalent:

| Goal | Template | Extraction namespace | Result in Splunk |
|------|----------|----------------------|------------------|
| Preserve only the parsed message body | `t_msg_only` | `.tmp.*` for internal values | `${MSGONLY}` |
| Preserve parsed header plus message | `t_hdr_msg` | `.tmp.*` for internal values | `${MSGHDR}${MESSAGE}` |
| Preserve program, PID, and message | `t_program_msg` | `.tmp.*` for internal values | Reconstructed program/PID plus message |
| Preserve RFC5424 header and SDATA | `t_hdr_sdata_msg` or `t_5424_hdr_sdata_compact` | `.tmp.*` for internal values | Reconstructed RFC5424 content; not necessarily original wire bytes |
| Replace the body with normalized key/value text | `t_kv_values` | `.values.*` | WELF-formatted values, native `.SDATA.*`, and `.metadata.*` |
| Replace the body with JSON | `t_json_values` | `.values.*` | JSON values, native `.SDATA.*`, and `.metadata.*` |
| Include parsed values and original message as a field | `t_kv_values_msg` or `t_json_values_msg` | `.values.*` | Transformed WELF or JSON with a `message` field |
| Preserve a raw-message form and send indexed HEC fields | Appropriate raw-message template | `fields.*` | Selected message representation plus indexed HEC fields |

Apply these namespace rules:

- Use `.tmp.*` for intermediate fragments, discarded prefixes, and raw tails that must not appear in the event.
- Use `.values.*` only for fields intentionally serialized by a values template.
- Native RFC5424 structured data is already available under `.SDATA.*`; values templates serialize it without reparsing the complete `${SDATA}` string.
- Use `fields.*` only when indexed HEC fields are required. This is destination-specific and is not a Splunk search-time field definition.
- Never capture an unparsed tail such as `key="value" key2="value with spaces"` into `.values.*` when using a values template. Parse the individual values and keep the raw tail in `.tmp.*`.

### Parser methods

**`kv-parser`** parses key/value input. Do not apply it to native RFC5424 `${SDATA}` merely to expose fields that already exist in `.SDATA.*`. Use it for an actual KV message or a deliberately isolated nonstandard KV tail.

```conf
parser {
    kv-parser(
        prefix('.values.')
        template('${MESSAGE}')
        pair-separator(' ')
        value-separator('=')
    );
};
```

Set `template()` to a `.tmp.*` field when only part of a message is KV data. Change `pair-separator()` or `value-separator()` only when the source format requires it.

**`csv-parser`** parses stable positional layouts. Set `template()` when the delimited data is not the entire message. Use `flags(greedy)` only when the final column should consume the remainder, and `flags(drop-invalid)` only when invalid column counts should drop the event.

```conf
parser {
    csv-parser(
        columns('col1', 'col2', 'col3')
        prefix('.values.')
        delimiters(',')
        quote-pairs('""')
        flags(escape-double-char)
    );
};
```

**`regexp-parser`** parses structured input that is not reliably KV or positional:

```conf
parser {
    regexp-parser(
        template('${MESSAGE}')
        patterns('^(?<field1>\d+) (?<field2>[^ ]+) (?<field3>.*)')
        prefix('.tmp.')
    );
};
```

**`json-parser`** parses JSON from `MESSAGE` or another selected field when the base JSON topic has not already populated the required values:

```conf
parser { json-parser(prefix('.values.') template('${MESSAGE}')); };
```

**`date-parser`** parses a timestamp from a selected field:

```conf
parser {
    date-parser(
        format('%s.%f', '%s')
        template('${.tmp.timestamp}')
    );
};
```

**`syslog-parser`** reparses a reconstructed syslog line, commonly after `regexp-parser` and `date-parser` in an almost-syslog normalizer:

```conf
parser {
    syslog-parser(
        flags(assume-utf8, guess-timezone)
        template('${.tmp.pri} $S_ISODATE ${.tmp.message}')
    );
};
```

Combine methods or use conditional branches when samples contain multiple stable variants.

### Regular-expression quoting

Prefer single-quoted syslog-ng strings for regular expressions when the pattern does not contain an apostrophe:

```conf
# Single-quoted string: literal quotes and regex backslashes.
patterns('rc="(?<rc>[^"]*)" and count=(?<count>\d+)')

# Equivalent double-quoted string: escape quotes and regex backslashes.
patterns("rc=\"(?<rc>[^\"]*)\" and count=(?<count>\\d+)")
```

These examples are final `.conf` content. MCP or JSON transport can display additional backslashes; do not copy transport-level escapes into the parser.

## Complete minimal example: RFC5424 with native SDATA

This routing-only example preserves RFC5424 structured data. It does not reparse SDATA into `.values.*` because `t_5424_hdr_sdata_compact` consumes the native `${SDATA}` value directly.

```conf
block parser app-syslog-thinkst_canary() {
    channel {
        rewrite {
            r_set_splunk_dest_default(
                index('netfw')
                sourcetype('thinkst:canary')
                vendor('thinkst')
                product('canary')
                template('t_5424_hdr_sdata_compact')
            );
        };
    };
};

application app-syslog-thinkst_canary[sc4s-syslog-sdata] {
    filter {
        filter(f_is_rfc5424)
        and program('ThinkstCanary' type(string))
        and match('@51136' value('SDATA') type(string) flags(substring));
    };
    parser { app-syslog-thinkst_canary(); };
};
```

To transform this event into JSON or WELF, select the corresponding values template, which already includes native `.SDATA.*`. To preserve this representation and add indexed fields, map only the requested values to `fields.*`.

## Authoring checklist

- Confirm the framing, payload format, application topic, and topic precedence.
- Confirm whether body-only, header-plus-message, RFC5424 SDATA, WELF, or JSON output is required.
- Confirm every requested field and its exact expected value for each sample.
- Keep intermediate fragments and unparsed tails in `.tmp.*`.
- Do not duplicate native `.SDATA.*` unless a nonstandard tail genuinely requires reparsing.
- Ensure the selected output template consumes the namespace used for final fields.
- Add a post-parse validation filter when metadata assignment depends on successful extraction.
- Inspect literal quotes and backslashes in the final `.conf`, not its JSON-serialized representation.
- For the full template list, inspect `t_templates.conf` in the version-matched SC4S package.

## Deployment path

- Deploy to a running SC4S instance: `/opt/sc4s/local/config/app_parsers/<filename>`
- Restart SC4S after deploying: `sudo systemctl restart sc4s` or `docker restart sc4s`
