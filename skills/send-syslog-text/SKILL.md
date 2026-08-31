---
name: sc4s-send-syslog
description: Send raw-text test syslog events to the SC4S host through its MCP tool. Use when a user wants to inject sample syslog lines for parser, routing, or ingestion testing; not for PCAP replay or arbitrary hosts.
---

# Send Syslog Text

Use this skill to inject user-supplied test events into the SC4S instance
connected through MCP.

## Discover the tool

Find a callable tool whose name ends with `send_syslog_text`. Store everything
before that suffix as `{SC4S_NS}` and call `{SC4S_NS}send_syslog_text`.

If the tool is unavailable, explain that sending requires an SC4S MCP
connection with the event-sending tool enabled. Do not substitute a shell
command, a local socket connection, or another destination.

## Prepare the request

- Use the user's raw text exactly. Each non-empty line is one syslog event.
- Default to UDP when the user does not specify a protocol.
- Default to port `514` when the user does not specify one. The MCP server may
  reject a port outside its configured allowlist.
- Omit `framing` unless the user specifies it. TCP then uses newline framing;
  UDP sends raw datagrams. For TCP captures or systems that require RFC 6587
  octet counting, pass `framing="octet-counting"` only when requested or known.
- Use the tool's default timeout unless the user provides a reason to change it.

The destination host is deliberately not an argument: the tool derives it from
the SC4S MCP server's `SC4S_API_URL`. Do not attempt to send to a different
host.

## Confirm before sending

Sending injects events into a running SC4S instance. Before the tool call,
show the event count, protocol, port, and framing, then obtain explicit
confirmation.

## Send and report

Call `{SC4S_NS}send_syslog_text` once with the prepared arguments.

Report `attempted`, `sent`, `failed`, protocol, framing, and port from the
result. A successful response confirms only that the MCP server handed bytes
to its socket. It does not prove that SC4S parsed, routed, indexed, or
delivered the events.

For an error response, show its message and stop. Do not retry automatically.
