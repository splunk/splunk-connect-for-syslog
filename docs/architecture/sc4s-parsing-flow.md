# SC4S Parsing Flow and Parser Types

This document summarizes how logs are parsed in SC4S, based on:

- `package/etc/conf.d/sources/source_syslog/plugin.jinja`
- parser topic mappings in `package/etc/conf.d/plugin/app_parser_topics.conf`
- parser implementations in `package/etc/conf.d/conflib`

## High-level parsing flow

For syslog sources, SC4S follows this general path:

1. Ingest on configured source ports (UDP/TCP/TLS or RFC syslog ports).
2. Parse wire format:
   - Try strict RFC5424 first on generic network sources.
   - Fall back to RFC3164/almost-syslog normalization.
   - Fall back again to raw parser group for malformed/non-standard events.
3. Normalize host and source metadata:
   - host fixes/cache/reverse DNS (if enabled)
   - host lowercase normalization
   - source mapping (`.netsource.*`) via explicit source settings or contextual lookup
4. Route through parser topics in order:
   - `sc4s-syslog-sdata`
   - `sc4s-syslog-pgm`
   - `sc4s-syslog`
   - `sc4s-network-source`
   - `fallback`
5. Apply post-processing (`sc4s-postfilter`, `sc4s-finalfilter`) in destination log paths.
6. Send to destination (HEC/syslog/etc.), unless routed to null queue.

## Topic routing behavior in `plugin.jinja`

When an event is not yet identified (`not filter(f_is_source_identified)`), SC4S uses:

- `sc4s-syslog-sdata` if structured SDATA exists.
- `sc4s-syslog-pgm` if SDATA path did not match and `$PROGRAM` is non-empty.
- `sc4s-syslog` if both previous branches did not match.

Then SC4S attempts `sc4s-network-source`, and finally `fallback`.

### `sc4s-syslog` vs `sc4s-syslog-pgm`

- `sc4s-syslog-pgm` is used when the `PROGRAM` field exists and is suitable for parser selection.
- `sc4s-syslog` is used when `PROGRAM` is empty/not useful, and matching must rely on generic message/body patterns.

In practice, many vendor parsers with `program(...)` filters live on `sc4s-syslog-pgm`, while message-signature parsers often live on `sc4s-syslog`.

## Main parser families in `conflib`

The parser library is organized by function:

- `syslog` (110 files): main vendor/product syslog parsers.
- `netsource` (38 files): source-based routing using `.netsource.*` and source tags.
- `almost-syslog` (19 files): repair near-syslog formats into parseable syslog.
- `raw` (6 files): process malformed/non-standard raw events.
- `fallback` (4 files): catch-all defaults when nothing else matches.
- `post-filter` (15 files): late event adjustments before destination.
- `cef` (32 files): CEF-specific subtype parsers.
- `cisco-syslog` (10 files): Cisco percent-code family parsers.
- `json` (2 files): JSON family parsers.
- `leef` (1 file): LEEF family parser.

## Topic definitions

`package/etc/conf.d/plugin/app_parser_topics.conf` maps parser groups to app-parser topics:

- `app-group-sc4s-almost-syslog` -> `sc4s-almost-syslog`
- `app-group-sc4s-syslog-sdata` -> `sc4s-syslog-sdata`
- `app-group-sc4s-syslog-pgm` -> `sc4s-syslog-pgm`
- `app-group-sc4s-syslog` -> `sc4s-syslog`
- `app-group-sc4s-syslog-netsource` -> `sc4s-network-source`
- `app-group-sc4s-raw` -> `sc4s-raw-syslog`
- `app-group-sc4s-fallback` -> `fallback`
- `app-plugin-source-postprocess` -> `sc4s-postfilter`
- `app-plugin-source-finalprocess` -> `sc4s-finalfilter`

## Typical parser file structure

Most parser configs follow this pattern:

1. `application ...[topic]` with a filter match.
2. `block parser ...` implementing parsing/rewrites.
3. `r_set_splunk_dest_default(...)` to set defaults for:
   - `.splunk.index`
   - `.splunk.source`
   - `.splunk.sourcetype`
   - `fields.sc4s_vendor`, `fields.sc4s_product`, optional `fields.sc4s_class`
4. Optional subtype refinement via `r_set_splunk_dest_update_v2(...)`.
5. Optional timestamp correction, field cleanup, and message normalization.

## End-to-end log path (compact)

`Ingress` -> `RFC5424 or RFC3164/almost/raw` -> `metadata normalization` -> `syslog-sdata/pgm/syslog` -> `netsource` -> `fallback` -> `postfilter/finalfilter` -> `destination`.
