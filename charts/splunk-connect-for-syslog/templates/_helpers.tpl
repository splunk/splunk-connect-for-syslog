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
Space-separated names of the env vars the StatefulSet sets itself. Keep in sync with
statefulset.yaml: env may not repeat them, because server-side apply rejects
duplicate env names.
*/}}
{{- define "splunk-connect-for-syslog.managedEnvNames" -}}
{{- $names := list "SC4S_SNMP_TRAP_COLLECT" "SC4S_CONTAINER_HOST" "SC4S_RUNTIME_ENV" "SC4S_SOURCE_TLS_ENABLE" -}}
{{- range list "TCP" "UDP" "RFC6587" "RFC5426" "TLS" "RFC5425" -}}
{{- $names = append $names (printf "SC4S_LISTEN_DEFAULT_%s_PORT" .) -}}
{{- end -}}
{{- range list "URL" "TOKEN" "TLS_VERIFY" "DISKBUFF_ENABLE" -}}
{{- $names = append $names (printf "SC4S_DEST_SPLUNK_HEC_DEFAULT_%s" .) -}}
{{- end -}}
{{- if .Values.splunk.hec_tls -}}
{{- $names = append $names "SC4S_DEST_SPLUNK_HEC_DEFAULT_TLS_MOUNT" -}}
{{- end -}}
{{- with .Values.sc4s.proxy -}}
{{- if .http }}{{ $names = append $names "http_proxy" }}{{ end -}}
{{- if .https }}{{ $names = append $names "https_proxy" }}{{ end -}}
{{- if .no_proxy }}{{ $names = append $names "no_proxy" }}{{ end -}}
{{- end -}}
{{- range $vp := .Values.sc4s.vendor_product -}}
{{- range $type, $ports := $vp.ports -}}
{{- if $ports }}{{ $names = append $names (printf "SC4S_LISTEN_%s_%s_PORT" (upper $vp.name) (upper $type)) }}{{ end -}}
{{- end -}}
{{- with $vp.options }}{{ range $key, $_ := .listen }}{{ $names = append $names (printf "SC4S_LISTEN_%s_%s" (upper $vp.name) (upper $key)) }}{{ end }}{{ end -}}
{{- end -}}
{{- join " " $names -}}
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
