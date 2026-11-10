{{/*
Expand the name of the chart.
*/}}
{{- define "splunk-connect-for-syslog.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "splunk-connect-for-syslog.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "splunk-connect-for-syslog.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "splunk-connect-for-syslog.labels" -}}
helm.sh/chart: {{ include "splunk-connect-for-syslog.chart" . }}
{{ include "splunk-connect-for-syslog.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/component: "input"
app.kubernetes.io/part-of: "Splunk"
{{- end }}

{{/*
Selector labels
*/}}
{{- define "splunk-connect-for-syslog.selectorLabels" -}}
app.kubernetes.io/name: {{ include "splunk-connect-for-syslog.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "splunk-connect-for-syslog.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "splunk-connect-for-syslog.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
The renamed settings, resolved: EKS add-on settings must be camelCase, so hec_url became
hecUrl and so on. The old snake_case names still work; when both are set, the camelCase
name wins. Templates read these through
  {{- $cfg := include "splunk-connect-for-syslog.settings" . | fromYaml }}
*/}}
{{- define "splunk-connect-for-syslog.settings" -}}
{{- $s := .Values.splunk | default dict -}}
{{- $c := .Values.sc4s | default dict -}}
{{- $p := $c.proxy | default dict -}}
hecUrl: {{ ternary $s.hecUrl $s.hec_url (hasKey $s "hecUrl") | default "" | toJson }}
hecToken: {{ ternary $s.hecToken $s.hec_token (hasKey $s "hecToken") | default "" | toJson }}
hecVerifyTls: {{ ternary $s.hecVerifyTls $s.hec_verify_tls (hasKey $s "hecVerifyTls") | toJson }}
hecTls: {{ ternary $s.hecTls $s.hec_tls (hasKey $s "hecTls") | default "" | toJson }}
vendorProduct: {{ ternary $c.vendorProduct $c.vendor_product (hasKey $c "vendorProduct") | toJson }}
contextFiles: {{ ternary $c.contextFiles $c.context_files (hasKey $c "contextFiles") | toJson }}
configFiles: {{ ternary $c.configFiles $c.config_files (hasKey $c "configFiles") | toJson }}
proxy:
  http: {{ $p.http | toJson }}
  https: {{ $p.https | toJson }}
  noProxy: {{ ternary $p.noProxy $p.no_proxy (hasKey $p "noProxy") | toJson }}
{{- end }}

{{/*
Old snake_case setting names in use, one "old -> new" per line, for the install notes.
*/}}
{{- define "splunk-connect-for-syslog.deprecatedSettings" -}}
{{- $renames := list
  (list "splunk" "hec_url" "hecUrl") (list "splunk" "hec_token" "hecToken")
  (list "splunk" "hec_verify_tls" "hecVerifyTls") (list "splunk" "hec_tls" "hecTls")
  (list "sc4s" "vendor_product" "vendorProduct") (list "sc4s" "context_files" "contextFiles")
  (list "sc4s" "config_files" "configFiles") -}}
{{- range $renames -}}
{{- if hasKey (get $.Values (index . 0) | default dict) (index . 1) }}
  {{ index . 0 }}.{{ index . 1 }} -> {{ index . 0 }}.{{ index . 2 }}
{{- end -}}
{{- end -}}
{{- if hasKey ((.Values.sc4s | default dict).proxy | default dict) "no_proxy" }}
  sc4s.proxy.no_proxy -> sc4s.proxy.noProxy
{{- end -}}
{{- end }}

{{/*
Space-separated names of the env vars that env may not set: the ones the StatefulSet
sets itself (keep in sync with statefulset.yaml; server-side apply rejects duplicate
env names), plus the health check address, which the chart's health port and the
add-on's NLB health check assume is 0.0.0.0:8080.
*/}}
{{- define "splunk-connect-for-syslog.managedEnvNames" -}}
{{- $cfg := include "splunk-connect-for-syslog.settings" . | fromYaml -}}
{{- $names := list "SC4S_SNMP_TRAP_COLLECT" "SC4S_CONTAINER_HOST" "SC4S_RUNTIME_ENV" "SC4S_SOURCE_TLS_ENABLE" "SC4S_LISTEN_STATUS_PORT" "SC4S_LISTEN_STATUS_HOST" -}}
{{- range list "TCP" "UDP" "RFC6587" "RFC5426" "TLS" "RFC5425" -}}
{{- $names = append $names (printf "SC4S_LISTEN_DEFAULT_%s_PORT" .) -}}
{{- end -}}
{{- range list "URL" "TOKEN" "TLS_VERIFY" "DISKBUFF_ENABLE" -}}
{{- $names = append $names (printf "SC4S_DEST_SPLUNK_HEC_DEFAULT_%s" .) -}}
{{- end -}}
{{- if $cfg.hecTls -}}
{{- $names = append $names "SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_MOUNT" -}}
{{- end -}}
{{- if and (eq .Values.workload "daemonset") .Values.persistence.enabled -}}
{{- $names = append $names "SC4S_DEST_SPLUNK_HEC_DEFAULT_DISKBUFF_DISKBUFSIZE" -}}
{{- end -}}
{{- with $cfg.proxy -}}
{{- if .http }}{{ $names = append $names "http_proxy" }}{{ end -}}
{{- if .https }}{{ $names = append $names "https_proxy" }}{{ end -}}
{{- if .noProxy }}{{ $names = append $names "no_proxy" }}{{ end -}}
{{- end -}}
{{- range $vp := $cfg.vendorProduct -}}
{{- range $type, $ports := $vp.ports -}}
{{- if $ports }}{{ $names = append $names (printf "SC4S_LISTEN_%s_%s_PORT" (upper $vp.name) (upper $type)) }}{{ end -}}
{{- end -}}
{{- with $vp.options }}{{ range $key, $_ := .listen }}{{ $names = append $names (printf "SC4S_LISTEN_%s_%s" (upper $vp.name) (upper $key)) }}{{ end }}{{ end -}}
{{- end -}}
{{- join " " $names -}}
{{- end }}

{{/*
Bytes in a size such as "10Gi" or "50G" (whole numbers, K/M/G/T or Ki/Mi/Gi/Ti).
*/}}
{{- define "splunk-connect-for-syslog.quantityBytes" -}}
{{- $q := . -}}
{{- if kindIs "float64" $q }}{{ $q = int64 $q }}{{ end -}}
{{- $q = toString $q -}}
{{- if not (regexMatch "^[0-9]+([KMGT]i?)?$" $q) -}}
{{- fail (printf "persistence.size %q must be a whole number with an optional K, M, G, T, Ki, Mi, Gi or Ti suffix when workload is daemonset" $q) -}}
{{- end -}}
{{- $units := dict "" 1 "K" 1000 "M" 1000000 "G" 1000000000 "T" 1000000000000 "Ki" 1024 "Mi" 1048576 "Gi" 1073741824 "Ti" 1099511627776 -}}
{{- mul (regexReplaceAll "[^0-9]" $q "" | int64) (get $units (regexReplaceAll "^[0-9]+" $q "")) -}}
{{- end }}

{{/*
Disk buffer bytes per HEC worker, so that all workers together stay within persistence.size.
*/}}
{{- define "splunk-connect-for-syslog.diskBufferPerWorker" -}}
{{- $workers := .Values.env.SC4S_DEST_SPLUNK_HEC_DEFAULT_WORKERS | default 10 | int64 -}}
{{- div (include "splunk-connect-for-syslog.quantityBytes" .Values.persistence.size | int64) $workers -}}
{{- end }}

{{/*
Quotes an env value. YAML booleans become yes/no, the only form every SC4S
script accepts, and whole numbers keep their digits instead of float notation.
*/}}
{{- define "splunk-connect-for-syslog.envValue" -}}
{{- if kindIs "bool" . -}}
{{- ternary "yes" "no" . | quote -}}
{{- else if kindIs "float64" . -}}
{{- if eq . (float64 (int64 .)) }}{{ int64 . | quote }}{{ else }}{{ toString . | quote }}{{ end -}}
{{- else -}}
{{- toString . | quote -}}
{{- end -}}
{{- end }}
