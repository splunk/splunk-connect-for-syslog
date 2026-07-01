---
name: configurator-prompt-sync
description: Keeps the configure_sc4s MCP prompt in sync with the configurator tool logic. Use whenever configuration-tool.sh or sc4s_mcp/tools/configurator_tools.py is modified — added parameters, changed validation rules, changed hardware profiles, changed defaults, or any behavioural change.
---

# Configurator Prompt Sync

Whenever `configuration-tool.sh` or `sc4s_mcp/tools/configurator_tools.py` is changed, the `configure_sc4s` prompt in `sc4s_mcp/prompts/workflows.py` must be reviewed and updated to stay in sync.

## When this applies

Trigger this skill after any change to:
- `configuration-tool.sh` — new parameters, changed validation, new hardware profiles, changed defaults, new modes
- `sc4s_mcp/tools/configurator_tools.py` — new tool parameters, changed parameter names, changed validation logic, new return fields

## What to check

After modifying the configurator logic, review the `configure_sc4s` prompt in `sc4s_mcp/prompts/workflows.py` against the following checklist:

1. **Parameters** — does the prompt ask for every parameter that `sc4s_generate_config` accepts? Are any new parameters missing from the conversation flow?
2. **Validation rules** — if URL/token/timezone validation changed in the tool or script, does the prompt reflect the new rules and examples?
3. **Hardware profiles** — if profiles were added, removed, or renamed in `configuration-tool.sh`, does the prompt's hardware mode section match?
4. **Defaults** — if any default values changed, are the defaults shown to the user in the prompt still correct?
5. **Branching logic** — if new conditional sections were added (e.g. a new protocol option, a new mode), does the prompt's step-by-step flow cover them?
6. **Warnings** — if the tool now returns new warning types, does the prompt tell the LLM to surface them?

## What to do

For each item in the checklist that is out of sync:
1. Update the relevant section of the `configure_sc4s` prompt in `sc4s_mcp/prompts/workflows.py`
2. Keep the one-question-at-a-time constraint and the branching structure intact
3. Commit the prompt update together with the logic change in the same commit, or as an immediate follow-up

## Do not

- Do not leave the prompt stale after changing tool parameters — a prompt that asks for parameters the tool no longer accepts, or omits parameters the tool requires, will silently produce broken configs
