---
name: create-parser
description: "Turn a raw log sample into a deployed syslog-ng SC4S parser. Works with or without the SC4S MCP server."
---

# SC4S Create Parser Skill

Guide the operator through building and deploying a syslog-ng parser from a raw log sample.

## Step 1 — Detect MCP mode

Search your available tools for any callable tool whose name ends in `add_parser` — it may appear under any namespace depending on how the SC4S MCP server is registered. Store the namespace prefix (everything before `add_parser`, for example `mcp__mcp-server__`) as `{SC4S_NS}` and use it for all SC4S tool calls in this session. Use the same prefix for `get_parser_creation_guide`, `list_vendors`, `list_vendor_parsers`, `get_parser`, `search_docs`, `list_custom_parsers`, `get_custom_parser`, `get_job_status`, and `sc4s_health`.

- If a matching tool is **found and callable**: you are in **MCP mode**. Use `{SC4S_NS}add_parser` and all other `{SC4S_NS}*` tools below.
- If **no matching tool is found**: you are in **Manual mode**. Use manual steps below. Do not mention this detection to the operator — just adapt silently.

## Step 2 — Collect log sample

Ask the operator:

> "Please paste one or more raw log lines from the device you want to parse. The more examples you can share, the better the parser will be."

Wait for the operator to paste samples. Do not proceed until you have at least one log line.

## Step 3 — Gather parser knowledge

**MCP mode:**
1. Call `{SC4S_NS}get_parser_creation_guide` to load the full SC4S parser creation guide.
2. Call `{SC4S_NS}list_vendors` to check if the vendor already has existing parsers.
3. If the vendor exists, call `{SC4S_NS}list_vendor_parsers(vendor)` to list their parsers, then `{SC4S_NS}get_parser(parser_name)` on the most relevant one — use it as a reference for structure and conventions.
4. Call `{SC4S_NS}search_docs(query)` with the vendor or product name to find any additional documentation.

**Manual mode:**
Read the parser creation guide from this skill's directory: `parser-guide.md` (located next to this SKILL.md file). It contains the correct SC4S parser structure, topic types, rewrite functions, parser methods, and a complete example. Do not rely on general syslog-ng knowledge — use that file.

## Step 4 — Generate the parser

Analyze the log sample(s) and produce a `.conf` file following SC4S conventions:

1. Identify the vendor and product from the log content
2. Pick a filter that uniquely identifies this log source (program field preferred; message content as fallback)
3. Write the complete `.conf` file
4. Choose a filename: `<vendor>_<product>.conf` (lowercase, underscores, no spaces)

Show the complete generated parser to the operator and explain:
- What the filter matches and why
- What `vendor_product` value was chosen
- What Splunk sourcetype will be assigned (or how to add one via `sc4s:configure`)

Ask: "Does this parser look correct? Would you like any adjustments before I deploy it?"

Wait for confirmation. If the operator wants changes, revise and show the updated parser. Repeat until approved.

## Step 5 — Deploy

After the operator confirms the parser is correct:

**MCP mode:**

1. Call `{SC4S_NS}list_custom_parsers` before making any change.
2. If `<filename>.conf` already exists, call `{SC4S_NS}get_custom_parser` and show the operator what will change. Warn that deployment replaces that parser's complete content. If it does not exist, explain that a new custom parser will be added.
3. Say: "I'm about to deploy `<filename>.conf` to SC4S and restart its runtime — proceed? (yes/no)"

Wait for explicit "yes" before proceeding.

On "yes":
1. Call `{SC4S_NS}add_parser` exactly once with `filename=<filename>.conf` and `content=<parser content>`.
2. Extract and validate the returned `job_id`. Treat a missing or malformed job ID as an unsuccessful submission.
3. Call `{SC4S_NS}get_job_status(job_id)` and keep polling while the status is `in_progress`. Do not describe the parser as deployed or the restart as successful before a terminal result.
4. If the terminal status is `failed`, explain the reported error and stop. Do not claim success and do not retry or roll back without a separate explicit request and confirmation.
5. Only after terminal `success`, call `{SC4S_NS}get_custom_parser` to verify the deployed content and `{SC4S_NS}sc4s_health` to verify SC4S is healthy.
6. Report successful deployment only when the job succeeded and the post-change checks pass. If the parser cannot be read back or SC4S is unhealthy, report that the job completed but verification failed, then give the relevant recovery steps below.

If the deploy call fails:
- Translate the error to plain language — never show raw API responses
- Offer to show the parser content so the operator can deploy manually instead

If deployment returns a `409 conflict`, explain that another configuration job is active. Poll that job when its ID is available. After it completes, call `list_custom_parsers` and `get_custom_parser` again, rebuild the preview, and obtain fresh explicit confirmation before retrying. Do not treat the active job as this parser deployment.

**Manual mode:**

Say:

> "To deploy this parser manually:
> 1. Save the file as `/opt/sc4s/local/<filename>.conf`
> 2. Restart SC4S: `sudo systemctl restart sc4s` (or `docker restart sc4s` if running in Docker)
> 3. Check the logs: `sudo journalctl -u sc4s -f` (or `docker logs -f sc4s`)
> 4. Send a test log and verify it appears in Splunk with the correct sourcetype."

Then show the complete file content in a code block for easy copy-paste.

## Error Handling

| Situation | Response |
|-----------|----------|
| Deploy fails with auth error | "SC4S rejected the request — check that the MCP server token matches SC4S configuration." |
| SC4S unhealthy after deploy | "The parser may have a syntax error. Check `/opt/sc4s/local/<filename>.conf` and look for syslog-ng config errors in `sudo journalctl -u sc4s`." |
| API unreachable | "SC4S doesn't seem to be running. Try: `curl http://localhost:8080/health`" |
| Operator pastes malformed logs | Ask for clarification: "These logs look incomplete — can you paste the full log line including the syslog header?" |
