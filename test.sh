#
#  HEC=$(echo '{{- getenv "SPLUNK_HEC_URL" | strings.ReplaceAll "/services/collector" "" | strings.ReplaceAll "/event" "" | regexp.ReplaceLiteral "[, ]+" "/services/collector/event " }}/services/collector/event' | gomplate | cut -d' ' -f 1)

SPLUNK_HEC_URL="https://hec-inputs.splunk.local/services/collector/event"