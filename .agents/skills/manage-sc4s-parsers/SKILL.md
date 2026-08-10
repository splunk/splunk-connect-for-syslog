---
name: manage-sc4s-parsers
description: Safely list, inspect, deploy, update, or delete custom parsers on a running SC4S instance through MCP. Use for custom parser inventory, parser content review, parser replacement, removal, and post-change verification.
---

# Manage SC4S Parsers

Manage already-authored custom parser files on a live SC4S instance. When the user supplies raw logs and needs a new parser designed, use the `create-parser` skill instead.

## Discover the SC4S tools

Find a callable tool whose name ends with `list_custom_parsers`. Store everything before that suffix as `{SC4S_NS}`. Use the same prefix for `get_custom_parser`, `add_parser`, `delete_parser`, `get_job_status`, and `sc4s_health`.

If no matching tool is callable, explain that live parser management requires an SC4S MCP connection and stop before proposing a live mutation.

## Normalize parser names

Use a basename ending in `.conf`. Reject path separators, traversal components, empty names, or non-`.conf` extensions. Pass the normalized basename to every parser tool.

## List or inspect parsers

- For inventory, call `{SC4S_NS}list_custom_parsers` and present the returned names.
- For content inspection, first call `list_custom_parsers`, then call `{SC4S_NS}get_custom_parser(name)` only for a listed parser.

Read-only operations require no mutation confirmation.

## Deploy or update a parser

Before calling `add_parser`:

1. Call `{SC4S_NS}list_custom_parsers` to establish current state.
2. If the filename exists, call `{SC4S_NS}get_custom_parser` and show a focused diff plus the complete proposed replacement. State that `add_parser` replaces the parser's entire content.
3. If the filename is new, show its complete content and state that a new custom parser will be added.
4. Inspect the proposed content for obvious incompleteness, filename mismatch, and SC4S parser conventions. Do not invent missing parser logic; use `create-parser` when authoring is required.
5. Explain that applying the parser restarts SC4S and obtain fresh explicit confirmation immediately before the mutation.
6. Call `{SC4S_NS}add_parser(filename=<name>, content=<complete content>)` exactly once.
7. Require a valid `job_id`, then poll `{SC4S_NS}get_job_status(job_id)` while status is `in_progress`.
8. On terminal `failed`, report the error and stop without retry or automatic rollback.
9. On terminal `success`, call `{SC4S_NS}get_custom_parser(name)` and compare its content with the submitted content, then call `{SC4S_NS}sc4s_health`.

Report full success only when the job succeeded, the content matches, and SC4S is healthy.

## Delete a parser

Before calling `delete_parser`:

1. Call `{SC4S_NS}list_custom_parsers` and verify the exact name exists.
2. Call `{SC4S_NS}get_custom_parser(name)` and retain its exact content in the conversation as the rollback payload.
3. Show the exact filename, explain that the full custom parser will be removed and SC4S restarted, and obtain fresh explicit confirmation immediately before deletion.
4. Call `{SC4S_NS}delete_parser(name)` exactly once.
5. Require a valid `job_id`, then poll `{SC4S_NS}get_job_status(job_id)` while status is `in_progress`.
6. On terminal `failed`, report the error and do not retry.
7. On terminal `success`, call `{SC4S_NS}list_custom_parsers` to verify absence and `{SC4S_NS}sc4s_health` to verify runtime health.

Never automatically recreate a deleted parser. If rollback is requested later, preview the retained content and obtain new confirmation before calling `add_parser`.