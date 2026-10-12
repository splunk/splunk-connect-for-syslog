# SC4S handoff

Prepare a short handoff when SC4S evidence points to another owner or the collector issue remains unresolved. For active drops, imminent buffer exhaustion, repeated crashes/OOM, or a broad outage, flag urgency using available evidence; do not wait for a complete bundle.

Use existing evidence. Include only the relevant symptom, SC4S release if known, timestamped log/counter/sample, checks and results, current impact, and the precise help needed. Do not collect extra versions, topology, full configuration, or Splunk diagnostics solely to fill a template.

```text
SC4S issue: <symptom and affected scope; ongoing or mitigated>
Evidence: <time, exact collector error/counter trend; release if known>
Checked/changed: <relevant actions and results; job status if applicable>
Boundary: <SC4S component or external owner; uncertainty if unresolved>
Requested help: <specific next action/decision>
```

For a receiver rejection, give the destination, intended index when relevant, exact SC4S error/status, and queue trend to the Splunk owner. For no packets at the collector, give the source/protocol/port and capture interval to the sender/network owner. Stop troubleshooting that external system.

For a reproduced SC4S software defect, use the [repository escalation template](https://github.com/splunk/splunk-connect-for-syslog/blob/main/.github/ISSUE_TEMPLATE/bug-escalation-report.md) when requested, adding only relevant existing reproduction evidence. Prepare the handoff for the user; submit a ticket/message only when asked. Redact locally and keep customer captures/configuration out of public issues.
