---
name: create-parser
description: Design an SC4S syslog-ng parser from raw log samples, optionally deploy it through the SC4S MCP server. Use when onboarding a new vendor or product, adding a custom log source, or creating parser logic for unsupported logs.
---

# Create SC4S Parser

Guide the operator through collecting representative logs, designing an SC4S parser, optionally deploying it, and verifying the resulting event routing.

## 1. Collect requirements and samples

Ask once for all missing information:

- Full positive log lines. Prefer at least three examples covering different event types or layouts; require at least one.
- Vendor, product, and device or software version. Offer inferred values for confirmation when unknown.
- Desired Splunk index and sourcetype. Offer a conventional value for confirmation when unknown.
- Whether the parser should only route events or also parse named values into the event payload, and which values matter. Explain that this controls SC4S parser-stage extraction and output templates; it does not create Splunk search-time field definitions.

Do not proceed until at least one complete positive log, vendor, product, index, and sourcetype are known or explicitly confirmed. If only one positive example is available, continue but state that filter confidence is limited and request additional examples before production rollout.

## 2. Gather parser knowledge

Read `parser-guide.md` next to this file before designing the parser. Treat it as the authoritative reference for SC4S parser structure, filters, rewrites, templates, and deployment layout.

When the SC4S repository lookup tools are available:

1. Call `list_vendors` to check for existing vendor support.
2. When the vendor exists, call `list_vendor_parsers(vendor)`, then `get_parser(parser_name)` for the closest parser. Reuse conventions, not product-specific assumptions.
3. Call `search_docs(query)` with a narrow vendor, product, format, or parser question.

Use these lookups to supplement the bundled guide, not replace it.

## 3. Design the parser

Analyze every supplied sample and create a complete `.conf` file:

1. Identify RFC3164, RFC5424, CEF, or the supported format described by the guide.
2. Select the narrowest reliable application topic and filter. Prefer structured identity or program values over message-text matching. Account for the positive samples and avoid the supplied negative examples.
3. Select parser stages appropriate to the data and requested field extraction.
4. Set the confirmed index, sourcetype, vendor, product, and template through SC4S rewrite conventions.
5. Set `<filename>` to `app-<type>-<vendor>_<product>.conf`. Normalize it to lowercase, use underscores within vendor/product identifiers, retain the `.conf` suffix, and reject path separators, traversal components, or an empty name.

Show the exact `<filename>` and complete parser. Explain:

- The detected format, application topic, and filter.
- Why each positive sample should match and why negative examples should not.
- The selected index, sourcetype, `vendor_product`, template, and extracted fields.
- Any assumptions caused by missing samples or product information.

If an external metadata override is needed, recommend `$manage-splunk-metadata`; do not refer to an undefined `sc4s:configure` command.

Ask whether the parser needs adjustments. Revise and repeat the explanation until the operator approves the content. Treat this as authoring approval only, not permission to mutate SC4S.

## 4. Optionally deploy

Ask whether to deploy the approved parser.

If `$manage-sc4s-parsers` is available, hand off the exact approved `<filename>` and parser content to that skill. Follow its read-before-write, overwrite warning, fresh confirmation, asynchronous job polling, read-back, health verification, conflict handling, and rollback-preservation workflow. Do not call `add_parser` directly from this skill, and do not reuse authoring approval as deployment confirmation.

If the management skill is unavailable or the operator prefers manual deployment:

1. Save the file as `/opt/sc4s/local/config/app_parsers/<filename>`.
2. Restart the SC4S runtime using the operator's deployment method.
3. Inspect runtime logs for syslog-ng configuration or restart errors.

Always provide the complete parser content for manual copy and preserve the approved filename exactly.

## 5. Verify event routing

After either deployment path:

1. Send a positive sample through the same transport and source path used by the device.
2. Verify in Splunk that it arrives in the confirmed index and sourcetype with the intended vendor, product, template output, and requested extracted fields.
3. When a negative example exists, send or search for it and verify that the new parser did not route it into the new sourcetype.
4. If verification fails, report the observed mismatch and return to parser design. Do not redeploy a revision without a new preview and confirmation through `$manage-sc4s-parsers`.

Use precise completion language:

- Job success, exact read-back, and healthy SC4S means **deployed and runtime-verified**.
- A correctly routed positive sample with expected metadata and fields means **end-to-end verified**.
- If the operator cannot perform the Splunk check, report deployment status and state explicitly that end-to-end verification remains outstanding.
