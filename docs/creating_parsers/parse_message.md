# Parse Messages

!!! note "Prerequisites"
    Before reading this section, make sure you are familiar with [Sources](../sources/index.md) and [Read First](index.md).

This section covers how to create `block parser`. Every `application` block references a `block parser` that defines how to process the matched message. Within the parser, you extract fields and set Splunk metadata.

## Structure

```
block parser <parser-name>() {
    channel {
        parser { <parsing expressions> };
        rewrite { <setting new fields> };
    };
};
```

A block parser contains a `channel { }` with two stages:

1. **Parsing** (optional) — extract fields from the message using `kv-parser`, `csv-parser`, `regexp-parser`, `json-parser`, `date-parser`, or `syslog-parser`.
2. **Rewrite** — set Splunk destination metadata (index, sourcetype, vendor, product, template).

## Rewrite functions

There are two rewrite functions for setting Splunk metadata:

**`r_set_splunk_dest_default`** — sets all base Splunk metadata. Includes `index`, `sourcetype`, `vendor`, `product`, and optionally `source` and `template`.

```
rewrite {
    r_set_splunk_dest_default(
        index("netops")
        sourcetype("alcatel:switch")
        vendor("alcatel")
        product("switch")
        template("t_hdr_msg")
    );
};
```

**`r_set_splunk_dest_update_v2`** — overrides specific fields already set by `r_set_splunk_dest_default`. It accepts `index`, `source`, `sourcetype`, and `template` options. You can also use the `condition` option for a conditional expression.

```
rewrite {
    r_set_splunk_dest_update_v2(
        sourcetype('citrix:netscaler:appfw')
        condition(message(':(\s+\S+)?\s+APPFW(\s+\S+){3}\s+:'))
    );
};
```

## Templates

The `template` parameter in `r_set_splunk_dest_default` controls what part of the message is forwarded to Splunk. Templates are defined in [`package/etc/conf.d/conflib/_common/t_templates.conf`](https://github.com/splunk/splunk-connect-for-syslog/blob/main/package/etc/conf.d/conflib/_common/t_templates.conf). The most common ones:

| Template | Content | Use case |
|---|---|---|
| `t_hdr_msg` | `${MSGHDR}${MESSAGE}` | Default for most parsers |
| `t_msg_only` | `${MSGONLY}` | When header is not needed (e.g. Palo Alto) |
| `t_program_msg` | `${PROGRAM}[${PID}]: ${MESSAGE}` | Program with PID and message |
| `t_hdr_sdata_msg` | `${MSGHDR}${MSGID} ${SDATA} ${MESSAGE}` | RFC5424 with structured data |
| `t_json_values_msg` | Same as `t_json_values` + `message=$MSG` | Parsed fields as JSON with original message |

## Parsing methods

Parsers in syslog-ng control how incoming log messages are broken down and structured for further processing and field extraction. They analyze the message content, extracting meaningful data into named fields that can later be used in Splunk. Different log sources and formats require different parsing strategies:

**`kv-parser`** — use when logs contain key/value pairs (`key=value`).

Options:

- `prefix()` — string prepended to every extracted key name. Prevents collisions with built-in syslog-ng macros and keeps parsed fields in their own namespace. For example, with `prefix(".values.")`, a key `src=10.0.0.1` becomes the field `.values.src`.
- `template()` — specifies which part of the message to parse. By default, `kv-parser` operates on `${MESSAGE}`.
- `pair-separator()` — custom delimiter between key=value pairs (default is whitespace).
- `value-separator()` — custom separator between key and value (default is `=`).

```
# parsing HDR + MSG of the log and prepending parsed values with `.values.`
parser {
    kv-parser(prefix(".values.") template("$(template t_hdr_msg)"));
};
```

**`csv-parser`** — use when logs are consistently delimited with stable column order.

Options:

- `columns()` — comma-separated list of column names. Each column maps positionally to a delimited field in the message. Names become field keys (prefixed if `prefix()` is set).
- `prefix()` — string prepended to each column name (e.g., `prefix(".values.")` turns column `"src"` into `.values.src`).
- `delimiters()` — character(s) used to split the message into columns (e.g., `','` for CSV, `'\t'` for TSV). By default, space is used.
- `quote-pairs()` — characters used for quoting values that contain the delimiter (e.g., `'""'` for double-quote pairs).
- `template()` — specifies which part of the message to parse. By default, `csv-parser` operates on `${MESSAGE}`.
- `flags()` — parsing behavior flags:
    - `escape-double-char` — treat doubled characters as a literal char inside a value, e.g., use `,,` to escape a single comma `,`.
    - `greedy` — assign all remaining text to the last column instead of discarding it.
    - `drop-invalid` — drop the message if the number of fields does not match the column count.

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

**`regexp-parser`** — use to parse message content with regular expressions.

Options:

- `patterns()` — one or more regular expressions with named capture groups (`(?<name>...)`). Each named group becomes a field.
- `prefix()` — string prepended to each captured group name.
- `template()` — which part of the message to match against (default is `${MESSAGE}`).

```
parser {
    regexp-parser(
        template("${MESSAGE}")
        patterns("^(?<field1>\\d+) (?<field2>[^ ]+) (?<field3>.*)")
        prefix(".parsed.")
    );
};
```

**`json-parser`** — use when logs are JSON-formatted.

Options:

- `prefix()` — string prepended to each JSON key. Nested JSON objects are flattened with dots (e.g., `{"event":{"src":"10.0.0.1"}}` with `prefix(".values.")` becomes `.values.event.src`).
- `template()` — which field to parse as JSON (default is `${MESSAGE}`).

```
parser {
    json-parser(prefix('.values.'));
};
```

**`date-parser`** — use when the timestamp needs to be explicitly parsed from a field, e.g., from a non-syslog message.

Options:

- `format()` — one or more strptime format strings to try in order (e.g., `'%s.%f'` for epoch with fractional seconds, `'%Y-%m-%dT%H:%M:%S%z'` for ISO 8601). Multiple formats can be passed as a comma-separated list; the first one that matches wins.
- `template()` — which field contains the timestamp string to parse.

```
parser {
    date-parser(
        format('%s.%f', '%s')
        template("${.tmp.timestamp}")
    );
};
```

**`syslog-parser`** — re-parses a reconstructed syslog line. Used in almost-syslog parsers when the original message has a non-standard header that needs to be normalized first with `regexp-parser` and then re-parsed.

Options:

- `template()` — the string to parse as a syslog message. Typically composed from `.tmp.*` fields extracted by a prior `regexp-parser`.
- `flags()` — parsing behavior flags:
    - `assume-utf8` — assume the message is UTF-8 encoded without verification.
    - `guess-timezone` — attempt to guess the timezone if not explicitly present in the timestamp.
    - `no-header` — parse only the PRI field; put the rest into `${MSG}`.

```
# after regexp-parser extracted parts into .tmp.* fields
parser {
    syslog-parser(
        flags(assume-utf8, guess-timezone)
        template("${.tmp.pri} $S_ISODATE ${.tmp.message}")
    );
};
```

## Rewrite operations

Beyond `r_set_splunk_dest_default` and `r_set_splunk_dest_update_v2`, block parsers commonly use these rewrite operations:

**`set()`** — sets a field to a value. Supports macro expansion and conditions.

```
rewrite {
    # copy a parsed field into HOST
    set("${.values.hostname}", value("HOST"));

    # conditional set
    set("new_value", value("PROGRAM") condition(program('old_value' type(string))));
};
```

**`subst()`** — performs string substitution on a field value. Supports regex.

```
rewrite {
    # strip leading ": " from MESSAGE
    subst('^: ', "", value("MESSAGE"));

    # strip path prefix from PROGRAM (e.g., "/usr/bin/app" -> "app")
    subst('^\/(?:[^\/]+\/)+', "", value("PROGRAM"));

    # global flag to replace all occurrences
    subst('\t', " ", value("MESSAGE") flags(global));
};
```

**`unset()`** — removes a field entirely.

```
rewrite {
    unset(value("PROGRAM"));
    unset(value("PID"));
};
```

**`r_set_dest_splunk_null_queue`** — tags the message for dropping (null queue). Used in post-filters to discard noise or incomplete events.

```
rewrite(r_set_dest_splunk_null_queue);
```

**`map-value-pairs`** — remaps existing name-value pairs to a different set of names.

```
# map all .values.* to .SDATA.sc4sfields@27389.*, e.g., .values.src -> .SDATA.sc4sfields@27389.src
rewrite {
    map-value-pairs(
        key('.values.*' rekey(shift-levels(2) add-prefix(".SDATA.sc4sfields@27389.")))
    );
};
```

## Examples

**Simple parser** — no field extraction, just sets Splunk metadata:

```
block parser app-syslog-alcatel_switch() {
    channel {
        rewrite {
            r_set_splunk_dest_default(
                index('netops')
                sourcetype('alcatel:switch')
                vendor("alcatel")
                product("switch")
                template('t_hdr_msg')
            );
        };
    };
};
```

**Parser with field extraction** — extracts key/value pairs, validates a required field:

```
block parser app-syslog-vendor_product() {
    channel {
        parser {
            kv-parser(prefix(".values.") template("$(template t_hdr_msg)"));
        };
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

**Parser with conditional branches** — routes different message types to different sourcetypes:

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
