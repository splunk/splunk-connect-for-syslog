#!/bin/bash
# Copies the SC4S image and pushes the EKS add-on chart to the AWS Marketplace ECR registry.
# Dry run by default; pass --push to upload. Requires AWS credentials for the
# splunk-marketplace seller account (for example from okta-aws-login).
#
#   eks_addon/release.sh [--push] [--chart-version VERSION]
set -euo pipefail

PUSH=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --push) PUSH=true; shift ;;
    --chart-version) export CHART_VERSION="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 1 ;;
  esac
done

for tool in aws helm yq jq docker; do
  command -v "${tool}" > /dev/null || { echo "Required command '${tool}' not found" >&2; exit 1; }
done

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/common.sh"

run() {
  if "${PUSH}"; then "$@"; else echo "[dry-run] $*"; fi
}

SRC_IMAGE="$(yq e '.image.repository' "${CHART_DIR}/values.yaml"):${CHART_APPVERSION}"
DEST_IMAGE="${ECR_IMAGE_REPO}:${CHART_APPVERSION}"
CHART_PACKAGE="${BUILD_DIR}/splunk-connect-for-syslog-${CHART_VERSION}.tgz"

prepare_chart
helm package "${EKS_CHART_DIR}" -d "${BUILD_DIR}"

if "${PUSH}"; then
  ecr_password="$(aws ecr get-login-password --region "${ECR_REGION}")"
  printf '%s' "${ecr_password}" | docker login --username AWS --password-stdin "${ECR_REGISTRY}"
  printf '%s' "${ecr_password}" | helm registry login --username AWS --password-stdin "${ECR_REGISTRY}"
  unset ecr_password

  if helm show chart "oci://${ECR_HELM_REPO}" --version "${CHART_VERSION}" > /dev/null 2>&1; then
    echo "Chart ${CHART_VERSION} already exists in ${ECR_HELM_REPO}; use --chart-version to push another version." >&2
    exit 1
  fi
fi

# Copies every platform in the source manifest list (linux/amd64 and linux/arm64).
run docker buildx imagetools create --tag "${DEST_IMAGE}" "${SRC_IMAGE}"
run helm push "${CHART_PACKAGE}" "oci://${ECR_HELM_NAMESPACE}"

echo
echo "Use these references in the Marketplace add-on version request:"
echo "  Helm chart: ${ECR_HELM_REPO}:${CHART_VERSION}"
echo "  Image:      ${DEST_IMAGE}"
