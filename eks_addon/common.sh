#!/bin/bash
# Shared settings and chart preparation for the SC4S EKS add-on build.
set -euo pipefail

EKS_ADDON_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CHART_DIR="${EKS_ADDON_DIR}/../charts/splunk-connect-for-syslog"
BUILD_DIR="${EKS_ADDON_DIR}/build"
EKS_CHART_OVERRIDES_DIR="${EKS_ADDON_DIR}/overrides"
EKS_CHART_DIR="${BUILD_DIR}/splunk-connect-for-syslog"

export CHART_VERSION="${CHART_VERSION:-$(yq e '.version' "${CHART_DIR}/Chart.yaml")}"
export CHART_APPVERSION="$(yq e '.appVersion' "${CHART_DIR}/Chart.yaml")"

# AWS Marketplace ECR. Repository names are assigned when the listing is created; these are placeholders.
ECR_REGION="us-east-1"
ECR_REGISTRY="709825985650.dkr.ecr.${ECR_REGION}.amazonaws.com"
export ECR_IMAGE_REPO="${ECR_REGISTRY}/splunk/images/splunk-connect-for-syslog"
ECR_HELM_NAMESPACE="${ECR_REGISTRY}/splunk/charts"
ECR_HELM_REPO="${ECR_HELM_NAMESPACE}/splunk-connect-for-syslog"

# Values hidden from the add-on configuration schema shown to customers.
SCHEMA_HIDDEN_PROPERTIES=(
  ".properties.image"
  ".properties.imagePullSecrets"
  ".properties.service.properties.usemetallb"
  ".properties.service.properties.metallbsharingkey"
)

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
}
