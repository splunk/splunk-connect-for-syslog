# Thales SafeNet Trusted Access (STA)

## Key facts

- Wire format: nominally RFC5424 but non-conformant. STA sets `APP-NAME`
and `PROCID` to the nil marker (`-`), places the STA source name (for
example `RemoteLogging`) in `MSGID`, and substitutes a UTF-8 BOM
(`EF BB BF`) for the structured-data slot before the JSON body. STA also
frames each message with RFC6587 octet-counting and emits the JSON body
pretty-printed across multiple lines.
- Vendor reference: [https://thalesdocs.com/sta/agents/logging/index.html](https://thalesdocs.com/sta/agents/logging/index.html)
- SC4S strips the BOM and forwards the JSON body as `_raw`.

## Sourcetypes


| sourcetype      | notes                                    |
| --------------- | ---------------------------------------- |
| thales:sta:json | JSON body emitted as `_raw`; BOM removed |


## Sourcetype and Index Configuration


| key        | sourcetype      | index   | notes                                                                 |
| ---------- | --------------- | ------- | --------------------------------------------------------------------- |
| thales_sta | thales:sta:json | netauth | Parsed via `app-netsource-thales_sta` on a dedicated `RFC6587_NOPARSE` listener |


## Why STA needs a dedicated listener

STA uses RFC6587 octet-counted framing, which requires the `syslog()`
driver to keep pretty-printed STA JSON messages intact — the standard
`*_TCP` / `*_UDP` listeners are newline-delimited and would fragment
every `\n` in the JSON body into a separate event. However, the regular
`RFC6587` listener cannot be used either: STA puts a UTF-8 BOM
(`EF BB BF`) in the SDATA slot, which is not a valid `STRUCTURED-DATA`
token, so the driver fails the whole message (`Error processing log message`).
`RFC6587_NOPARSE` sets the `no-parse` flag, so the driver only handles framing
and leaves the header alone. Moreover, the standard listener channels run a `syslog-parser()`
as the first step in the processing pipeline, which also rejects STA's header.
The `RFC6587_NOPARSE` channel skips this step entirely and goes
straight to `app-group-sc4s-syslog-netsource`, so the vendor netsource
parser always runs and owns header extraction.

## Enable the dedicated STA listener

Set a single environment variable on SC4S:

```
SC4S_LISTEN_THALES_STA_RFC6587_NOPARSE_PORT=602
```

The env-var shape is `SC4S_LISTEN_<VENDOR>_<PRODUCT>_RFC6587_NOPARSE_PORT`.
SC4S will:

- open TCP port 602 with the `syslog()` driver for RFC6587
octet-counted framing — the full wire message is delivered to the channel intact as `$MESSAGE`, with embedded newlines preserved,
- tag incoming events with `.netsource.sc4s_vendor=thales` and
`.netsource.sc4s_product=sta`,
- dispatch them **directly to `app-group-sc4s-syslog-netsource`** —
bypassing `app-group-sc4s-syslog-sdata` / `-pgm` / `-syslog` that the
standard channels try first — where `app-netsource-thales_sta`
regex-parses PRI, timestamp, host and `MSGID` out of `$MESSAGE`,
strips the BOM, and emits the JSON body with
`sourcetype=thales:sta:json` and `index=netauth`.

No custom source or log-path file is required.

## Tuning

The `RFC6587_NOPARSE` listener reuses the shared TCP tuning knobs
(`SC4S_SOURCE_LISTEN_TCP_SOCKETS`, `SC4S_SOURCE_TCP_MAX_CONNECTIONS`,
`SC4S_SOURCE_TCP_IW_SIZE`, `SC4S_SOURCE_TCP_FETCH_LIMIT`,
`SC4S_SOURCE_TCP_SO_RCVBUFF`). Any value you already set for regular TCP
listeners automatically applies here as well. See
`docs/architecture/fine-tuning.md` for the defaults and guidance.