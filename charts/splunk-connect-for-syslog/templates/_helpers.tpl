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
Pod-level securityContext.
Precedence: an explicit non-empty .Values.podSecurityContext always wins; else
when .Values.runAsNonRoot is true a non-root preset is applied; otherwise the
historical default (root, empty context) is used.
*/}}
{{- define "splunk-connect-for-syslog.podSecurityContext" -}}
{{- if .Values.podSecurityContext -}}
{{- toYaml .Values.podSecurityContext -}}
{{- else if .Values.runAsNonRoot -}}
runAsNonRoot: true
runAsUser: 1024
runAsGroup: 1024
fsGroup: 1024
seccompProfile:
  type: RuntimeDefault
{{- else -}}
{}
{{- end -}}
{{- end -}}

{{/*
Container-level securityContext.
Precedence: an explicit non-empty .Values.securityContext always wins; else when
.Values.runAsNonRoot is true a non-root preset is applied; otherwise the
historical default (root, empty context) is used. NET_BIND_SERVICE is added so
the default privileged ports (514/601) can bind as a non-root user.
*/}}
{{- define "splunk-connect-for-syslog.securityContext" -}}
{{- if .Values.securityContext -}}
{{- toYaml .Values.securityContext -}}
{{- else if .Values.runAsNonRoot -}}
allowPrivilegeEscalation: false
capabilities:
  drop:
    - ALL
  add:
    - NET_BIND_SERVICE
{{- else -}}
{}
{{- end -}}
{{- end -}}
