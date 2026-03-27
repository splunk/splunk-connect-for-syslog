# Filter Messages

!!! note "Prerequisites"
    Before reading this section, make sure you are familiar with [Sources](sources) and [Read First](index).

This section covers how to create `application` filters. Filters in user made parsers are responsible for matching incoming log messages based on a set of filter statements and routing them to the appropriate parsers for further processing.

Most filters have the following structure:

```
application <filter-name>[<topic>] {
    filter {
        <filter_body>
    };
    parser { <parser-name>(); };
};
```

Filters are grouped into topics. Each topic represents a stage or strategy for identifying log sources.

For example:

- **sc4s-syslog-sdata** - matches by structured data (often a Private Enterprise Number, PEN). Example:
```
application app-syslog-f5_bigip_structured[sc4s-syslog-sdata] {
    filter {
        match('^\[F5@12276' value("SDATA"));
    };
    parser { app-syslog-f5_bigip_structured(); };
};
```

- **sc4s-syslog-pgm** - matches by program value (`PROGRAM` in RFC3164, `APP-NAME` in RFC5424). Example:

```
application app-syslog-alcatel_switch[sc4s-syslog-pgm] {
    filter {
        program('swlogd' type(string) flags(prefix));
    };
    parser { app-syslog-alcatel_switch(); };
};
```

- **sc4s-syslog** - usually used for identification by message body content. Example:

```
application app-syslog-arista_eos[sc4s-syslog] {
    filter {
        program('^[A-Z]\S+$')
        and message('%' type(string) flags(prefix));
    };
    parser { app-syslog-arista_eos(); };
};
```

- **sc4s-network-source** - matches by destination port. Example:

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

- **cef** - for CEF-formatted messages. Example:

```
application app-cef-a10_vthunder[cef] {
    filter{
        match("A10" value(".metadata.cef.device_vendor"))
        and match("vThunder" value(".metadata.cef.device_product"));
    };
    parser { app-cef-a10_vthunder(); };
};
```

- **sc4s-almost-syslog** - for sources sending legacy non-conformant RFC 3164 logs.

Filters can use different functions to match parts of the log message. These functions can be combined in conditional patterns. Below is a list of the most common functions with their arguments, as well as common patterns for matching logs:

**program()**

Used for matching messages by the program field (`PROGRAM` in RFC3164, `APP-NAME` in RFC5424). You can pass the following options:

- `type()`:
    - `pcre` - Perl Compatible Regular Expressions (default).
    - `string` - Literal string match (faster than regex).
    - `glob` - Shell-style glob pattern.

- `flags()`:
    - `prefix` - Match if the value starts with the pattern.
    - `substring` - Match if pattern appears anywhere in the value.
    - `ignore-case` - Disable case-sensitive matching.

Example:

```
# using type(string) and flags(substring, ignore-case)
filter {
    program('avx-gw-state-sync' type(string) flags(substring, ignore-case))
};

# using default options (pcre regex)
filter {
    program('^[A-Z]\S+$')
};
```

**match()**

Used for matching messages against a pattern. Unlike `program()`, `match()` can target any field using the `value()` or `template()` parameters.

Syntax variants:

- `match(pattern)` - matches against the message header + message (`MSGHDR` + `MSG`).
- `match(pattern value("MACRO"))` - matches against a specific field.

Options:

- `type()`:
    - `pcre` - Perl Compatible Regular Expressions (default).
    - `string` - Literal string match (faster than regex).
    - `glob` - Shell-style glob pattern.

- `flags()`:
    - `prefix` - Match if the value starts with the pattern.
    - `substring` - Match if pattern appears anywhere in the value.
    - `ignore-case` - Disable case-sensitive matching.
    - `store-matches` - Store captured groups into `$0`–`$255` macros.

Examples:

```
# match by message body using regex (default type)
filter {
    message('^time=\d{10}\|hostname=')
};

# match a specific field using a literal string
# common use case for CEF-formatted logs
filter {
    match("A10" value(".metadata.cef.device_vendor"))
    and match("vThunder" value(".metadata.cef.device_product"));
};

# match against MSGHDR with regex
filter {
    match('(SYS|WF|TR|AUDIT|NF) ?$', value("MSGHDR"))
};

# match against structured data (SDATA)
filter {
    match('^\[F5@12276' value("SDATA"))
};
```

**message()**

A shorthand for `match(pattern value("MESSAGE"))` — matches only against the message body (`MSG`), excluding headers. Supports the same `type()` and `flags()` options as `match()`.

Example:

```
# literal substring match
filter {
    message(': Avi-Controller: ' type(string) flags(substring))
};
```

**host()**

Matches against the hostname field (`HOST`). Supports the same `type()` and `flags()` options as `program()`.

Example:

```
filter {
    host('myserver' type(string))
};
```

**String comparison operators (`eq`, `ne`)**

An alternative to `match()`, used for equality checks on macro values or environment variables. Two syntaxes exist depending on what is being resolved:

- `"${MACRO}"` — Resolves a macro value. Use for message fields like `${PROGRAM}`, `${HOST}`, or parser-set fields like `${.SDATA.sc4s@2620.product}`.
- `` "`ENV_VAR`" `` — Resolves an environment variable. Use for SC4S configuration options like `SC4S_DEST_*` or `SC4S_SOURCE_*`.

Available operators:

- `eq` — equals
- `ne` — not equals

Examples:

```
# check vendor_product from netsource enrichment
filter {
    "${.netsource.sc4s_vendor_product}" eq "aruba_clearpass"
};

# check if an env variable is set
filter {
    "`SC4S_DEST_BEYONDTRUST_SRA_SYSLOG_FMT`" eq "SDATA"
};
```

**tags()**

Used for filtering messages by tags. Tags are labels attached to messages and are fast to filter on compared to string matching. Custom tags can be added using `set-tag()` in rewrite rules.

Tags are set with:

```
rewrite r_set_my_tag {
    set-tag("my_tag");
};
```

Syntax:

- `tags("tag_name")` — matches if the message has the specified tag

Examples:

```
# match by source tag
filter {
    tags(".source.s_VMWARE_VCENTER")
};

# match by vendor/product tags
filter {
    tags("ns_vendor:vmware") and tags("ns_product:vsphere")
};

# match by wire format
filter {
    tags("wireformat:rfc3164_isodate")
};
```

**Conditional statements**

Filters can be combined using logical operators such as `and`, `or`, and `not`, and enclosed in parentheses for grouping complex conditions.

Examples:

```
# Match messages from the VMware vCenter source
# or by a combination of vendor and product tags
filter {
    tags(".source.s_VMWARE_VCENTER")
    or (
        tags("ns_vendor:vmware")
        and tags("ns_product:vsphere")
    )
};
```

## Send messages to parser

After creating filter, specify what parser should be use for further processing:

```
application app-syslog-vmware_cb-protect[sc4s-syslog] {
    filter {
        message('Carbon Black App Control event:  '  type(string)  flags(prefix));
    };  
    parser { app-syslog-vmware_cb-protect(); }; # If filtering succeeds send data to this parser
};
```

For more information about creating parsers see [Parse Messages](parse_message).