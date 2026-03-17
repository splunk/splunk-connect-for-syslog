# Splunk Monitoring Console health checks for SC4S

The Splunk Monitoring Console includes a Health Check feature that runs diagnostic searches against your Splunk deployment and reports results by severity: Error, Warning, Info, or Success. While the built-in checks focus on Splunk infrastructure (indexer status, disk usage, license health, queue saturation), you can create custom health checks to monitor SC4S data ingestion from the Splunk side.

This is useful because SC4S container logs show you what is happening on the **sender** side, while Monitoring Console health checks show you what is happening on the **receiver** side. When troubleshooting data flow issues, checking both sides gives the full picture.

For the official documentation, see [Access and customize health check](https://help.splunk.com/en/splunk-enterprise/administer/monitor/9.4/configure-the-monitoring-console/access-and-customize-health-check) in the Splunk Enterprise docs.

## How health checks work

Each health check item is a saved SPL search. When you click **Start** on the Health Check page, the searches run sequentially and produce results in three required columns:

| Column | Description |
|---|---|
| `instance` | The Splunk instance or host name |
| `metric` | A human-readable description of the result |
| `severity_level` | `0` = Success, `1` = Info, `2` = Warning, `3` = Error |

Results are sorted by severity so problems surface first.

## Creating a custom health check

1. Navigate to **Monitoring Console > Settings > Health Check Items**.
2. Click **New Health Check Item**.
3. Fill in the **Title** and **ID** fields.
4. Paste your search into the **Search** field. The search must include `| eval severity_level=` or results will show as N/A.
5. Add a **Description** explaining what the check does and how to remediate failures.
6. Click **Save**.

## Example: SC4S HEC ingestion errors

This check monitors Splunk internal logs for HTTP Event Collector warnings and errors that may indicate SC4S data is being rejected. Common causes include missing indexes, invalid tokens, or indexer overload.

| Field | Value |
|---|---|
| Title | SC4S HEC Ingestion Errors |
| ID | `sc4s_hec_errors` |

**Search:**

```
index=_internal sourcetype=splunkd source=*splunkd.log*
    (component=HttpInputDataHandler OR component=HttpEventCollector)
    (log_level=WARN OR log_level=ERROR)
    earliest=-15m
| stats count as error_count by host
| eval instance=host
| eval metric=error_count." HEC errors in last 15 min"
| eval severity_level=case(
    error_count >= 100, 3,
    error_count >= 10, 2,
    error_count >= 1, 1,
    1==1, 0
)
| fields instance metric severity_level
```

**Severity thresholds:**

| Condition | Severity |
|---|---|
| 100+ errors | Error |
| 10-99 errors | Warning |
| 1-9 errors | Info |
| 0 errors | Success |

**Description:** Monitors HEC-related warnings and errors on Splunk indexers over the last 15 minutes. A high error count typically means SC4S events are being rejected. Check container logs (`sudo podman logs SC4S`) for corresponding `4XX` status codes, and verify that all required SC4S indexes exist and that the HEC token is configured correctly.

## Turning a health check into an alert

You can convert any health check into a proactive scheduled alert:

1. Run the health check.
2. Click **Open in search**.
3. Add a filter such as `| where severity_level >= 2` to trigger only on warnings and errors.
4. Click **Save As > Alert** and configure a schedule and alert action (for example, email).

This lets you detect SC4S ingestion problems without manually running the health check.
