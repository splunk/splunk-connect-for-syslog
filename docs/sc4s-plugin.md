# SC4S Plugin

This plugin provides SC4S parser creation, configuration, troubleshooting, and live-management workflows for Codex, Claude Code, Cursor, and other agents that support Agent Skills.

The repository root is the plugin root, and `skills/` is the single source of skill content. Each client has a small native metadata directory: `.claude-plugin/` for Claude Code, `.codex-plugin/` for Codex, and `.cursor-plugin/` for Cursor. Codex's repository marketplace catalog lives in `.agents/plugins/marketplace.json`.

## Included skills

- `create-parser` creates SC4S syslog-ng parsers from raw log samples.
- `sc4s-guided-configuration` guides SC4S `env_file` configuration and tuning.
- `troubleshoot-sc4s` diagnoses health, ingestion, routing, parser, and configuration-job problems.
- `manage-splunk-metadata` safely manages full-replacement Splunk metadata overrides.
- `manage-sc4s-parsers` lists, inspects, deploys, updates, and deletes custom parsers with job polling and health verification.

## Use the skills

The agent can select a skill automatically when your request matches its description. To choose one explicitly, use the invocation syntax for your client:

| Client | Syntax | Example |
| --- | --- | --- |
| Codex | `$sc4s-plugin:<skill-name>` | `$sc4s-plugin:create-parser Create a parser for these log samples: ...` |
| Claude Code | `/sc4s-plugin:<skill-name>` | `/sc4s-plugin:create-parser Create a parser for these log samples: ...` |
| Cursor | `/<skill-name>` | `/create-parser Create a parser for these log samples: ...` |

In Codex, type `$` and select the skill from the suggestions. In Claude Code or Cursor, type `/` and select it from the command menu. Add the task details after the selected skill, including raw log samples, symptoms, or the configuration outcome you want.

You can also ask naturally without invoking a skill explicitly, for example: `Troubleshoot why SC4S is receiving events but not forwarding them to Splunk.` The client can then select `troubleshoot-sc4s` from its description.

## Install with Codex

Add this repository as a marketplace:

```shell
codex plugin marketplace add splunk/splunk-connect-for-syslog
codex plugin add sc4s-plugin@sc4s-plugins
```

The second command can instead be completed by installing **SC4S Plugin** from the Codex Plugins Directory. Restart Codex after installation so the skills are rediscovered.

## Install with Claude Code

Add this repository as a marketplace, then install the plugin:

```shell
claude plugin marketplace add splunk/splunk-connect-for-syslog
claude plugin install sc4s-plugin@sc4s-plugins
```

Reload an active Claude Code session after installation:

```text
/reload-plugins
```

Claude Code exposes the skills under the `sc4s-plugin` namespace, for example `/sc4s-plugin:create-parser`.

## Install with Cursor

Install directly from GitHub by running this command in Cursor Agent chat:

```text
/add-plugin https://github.com/splunk/splunk-connect-for-syslog
```

Teams and Enterprise administrators can instead import the GitHub repository from **Dashboard → Plugins → Add Marketplace → Import from Repo**. After installation, users enable the plugin for their preferred project or user scope from **Customize → Plugins**.

For local development, link the plugin root into Cursor and reload the window:

```shell
mkdir -p ~/.cursor/plugins/local
ln -s /path/to/splunk-connect-for-syslog ~/.cursor/plugins/local/sc4s-plugin
```
