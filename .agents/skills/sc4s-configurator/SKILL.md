---
name: sc4s-configurator
description: Configures SC4S by generating an env_file. Use when the user wants to configure SC4S, set up SC4S, generate a configuration, create an env_file, tune performance, set HEC URL/token, or says anything like "configure sc4s", "set up sc4s", "generate config", "create env_file".
---

# SC4S Configurator

When the user wants to configure SC4S, **do not ask questions yourself**. Instead, immediately invoke the `configure_sc4s` MCP prompt, which will guide the entire configuration conversation.

## How to invoke the prompt

Call the `configure_sc4s` MCP prompt. It will take over and guide the user through:

1. Choosing configuration mode (custom or hardware-based)
2. Collecting Splunk HEC URL and token
3. TLS settings
4. Protocol and performance tuning (based on mode)
5. Disk buffer settings
6. Timezone configuration
7. Generating the final `env_file` via `sc4s_generate_config`

## Do not

- Do not ask the user for HEC URL, token, or any other parameters yourself before invoking the prompt
- Do not call `sc4s_generate_config` directly without going through the prompt flow
- Do not skip the confirmation step in the prompt
