#!/bin/bash
# Shared settings and chart preparation for the SC4S EKS add-on build.
set -euo pipefail

EKS_ADDON_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CHART_DIR="${EKS_ADDON_DIR}/../charts/splunk-connect-for-syslog"
BUILD_DIR="${EKS_ADDON_DIR}/build"
EKS_CHART_OVERRIDES_DIR="${EKS_ADDON_DIR}/overrides"
EKS_CHART_DIR="${BUILD_DIR}/splunk-connect-for-syslog"

# Assigned before export: `export X="$(cmd)"` would hide a failing yq from set -e.
CHART_VERSION="${CHART_VERSION:-$(yq e '.version' "${CHART_DIR}/Chart.yaml")}"
CHART_APPVERSION="$(yq e '.appVersion' "${CHART_DIR}/Chart.yaml")"
if [[ -z "${CHART_VERSION}" || "${CHART_VERSION}" == "null" || -z "${CHART_APPVERSION}" || "${CHART_APPVERSION}" == "null" ]]; then
  echo "Could not read version/appVersion from ${CHART_DIR}/Chart.yaml (is mikefarah yq v4 installed?)" >&2
  exit 1
fi
export CHART_VERSION CHART_APPVERSION

# AWS Marketplace ECR. Repository names are assigned when the listing is created; these are placeholders.
ECR_REGION="us-east-1"
ECR_REGISTRY="709825985650.dkr.ecr.${ECR_REGION}.amazonaws.com"
export ECR_IMAGE_REPO="${ECR_REGISTRY}/splunk/images/splunk-connect-for-syslog"
ECR_HELM_NAMESPACE="${ECR_REGISTRY}/splunk/charts"
ECR_HELM_REPO="${ECR_HELM_NAMESPACE}/splunk-connect-for-syslog"

# Values customers cannot set on the add-on: removed from the add-on schema, which refuses unknown keys.
SCHEMA_HIDDEN_PROPERTIES=(
  ".properties.image"
  ".properties.imagePullSecrets"
  ".properties.service.properties.usemetallb"
  ".properties.service.properties.metallbsharingkey"
  # AWS lists these as settings add-ons should not let customers change.
  ".properties.nameOverride"
  ".properties.fullnameOverride"
  ".properties.podSecurityContext"
  ".properties.securityContext"
  ".properties.serviceAccount"
  # The add-on always runs as a DaemonSet; these only apply to the StatefulSet.
  ".properties.workload"
  ".properties.replicaCount"
  ".properties.autoscaling"
  ".properties.persistence.properties.storageClass"
  ".properties.persistence.properties.annotations"
)

# env names refused in the add-on schema because they look like credentials.
SCHEMA_SECRET_ENV_PATTERN="(TOKEN|PASSWORD|PASSWD|SECRET|PASSPHRASE|API_KEY|PRIVATE_KEY|token|password|passwd|secret|passphrase|api_key|private_key)"

prepare_chart() {
  echo "Preparing EKS add-on chart in ${EKS_CHART_DIR}"
  rm -rf "${BUILD_DIR}"
  mkdir -p "${BUILD_DIR}"
  cp -R "${CHART_DIR}" "${BUILD_DIR}/"

  # EKS add-ons do not run Helm hooks.
  rm -rf "${EKS_CHART_DIR}/templates/tests"

  local override target expanded="${BUILD_DIR}/override.tmp"
  for override in "${EKS_CHART_OVERRIDES_DIR}"/*.yaml; do
    target="${EKS_CHART_DIR}/$(basename "${override}")"
    yq e '(.. | select(tag == "!!str")) |= envsubst(nu)' "${override}" > "${expanded}"
    yq eval-all -i 'select(fileIndex == 0) * select(fileIndex == 1)' "${target}" "${expanded}"
  done
  rm -f "${expanded}"

  local schema="${EKS_CHART_DIR}/aws_mp_configuration_schema.json" prop
  cp "${EKS_CHART_DIR}/values.schema.json" "${schema}"
  for prop in "${SCHEMA_HIDDEN_PROPERTIES[@]}"; do
    jq "del(${prop})" "${schema}" > "${schema}.tmp" && mv "${schema}.tmp" "${schema}"
  done

  # Add-on settings must be camelCase: the chart's older snake_case names (hec_url,
  # vendor_product, ...) are dropped, and unknown keys are refused so they cannot slip in.
  jq '
    del(.properties.splunk.properties.hec_url, .properties.splunk.properties.hec_verify_tls,
        .properties.splunk.properties.hec_tls, .properties.sc4s.properties.vendor_product,
        .properties.sc4s.properties.context_files, .properties.sc4s.properties.config_files,
        .properties.sc4s.properties.proxy.properties.no_proxy)
    | .properties.sc4s.additionalProperties = false
    | .properties.sc4s.properties.proxy.additionalProperties = false
  ' "${schema}" > "${schema}.tmp" && mv "${schema}.tmp" "${schema}"

  # Add-on settings must not accept secrets. The HEC token comes from a Kubernetes Secret
  # (splunk.existingSecret), so hecToken/hec_token are refused, and so are env names that
  # look like credentials, for example a token for a second HEC destination.
  jq --arg secrets "${SCHEMA_SECRET_ENV_PATTERN}" '
    del(.properties.splunk.properties.hec_token, .properties.splunk.properties.hecToken)
    | .properties.splunk.additionalProperties = false
    | .properties.splunk.properties.existingSecret.description = "Name of the Kubernetes Secret that holds the HEC token. Create it in the add-on namespace before installing the add-on."
    | .properties.env.propertyNames = {"allOf": [.properties.env.propertyNames, {"not": {"pattern": $secrets}}]}
    | .properties.env.description += " Names that look like credentials (TOKEN, PASSWORD, SECRET and similar) are not accepted; put credentials in a Kubernetes Secret."
  ' "${schema}" > "${schema}.tmp" && mv "${schema}.tmp" "${schema}"

  # Helm validates the merged values, including the chart defaults for the hidden settings and
  # the k8version that AWS passes to helm template, so the packaged chart keeps open objects.
  cp "${schema}" "${EKS_CHART_DIR}/values.schema.json"

  # EKS validates only the customer's settings, so the add-on schema refuses unknown keys
  # everywhere: hidden settings and typos are rejected instead of silently applied.
  jq 'walk(if type == "object" and has("properties") and (has("additionalProperties") | not)
           then .additionalProperties = false else . end)' "${schema}" > "${schema}.tmp" && mv "${schema}.tmp" "${schema}"
}
