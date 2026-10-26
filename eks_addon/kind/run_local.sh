#!/bin/bash
# Local stand-in for installing the SC4S EKS add-on on a kind cluster. Renders the add-on
# chart the way EKS does (no hooks, settings checked against the schema) and applies it
# with server-side apply under the "eks" field manager.
#
#   HEC_URL=https://splunk:8088 HEC_TOKEN=<token> eks_addon/kind/run_local.sh up
#   eks_addon/kind/run_local.sh send      # send one TCP and one UDP test event
#   eks_addon/kind/run_local.sh status
#   eks_addon/kind/run_local.sh down      # delete the kind cluster
#
# Optional: SETTINGS_FILE (default settings.example.yaml), HEC_VERIFY_TLS (default no),
#           SC4S_IMAGE=repo:tag (local build, loaded into kind), KIND_CLUSTER, KIND_NODE_IMAGE.
set -euo pipefail

LOCAL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "${LOCAL_DIR}/../common.sh"

KIND_CLUSTER="${KIND_CLUSTER:-sc4s-addon}"
NAMESPACE="sc4s"
RELEASE="sc4s"
FULLNAME="${RELEASE}-splunk-connect-for-syslog"
SETTINGS_FILE="${SETTINGS_FILE:-${LOCAL_DIR}/settings.example.yaml}"
K=(kubectl --context "kind-${KIND_CLUSTER}")

up() {
  : "${HEC_URL:?set HEC_URL to the Splunk HEC endpoint}"
  : "${HEC_TOKEN:?set HEC_TOKEN}"
  export HEC_URL HEC_VERIFY_TLS="${HEC_VERIFY_TLS:-no}"

  if ! kind get clusters | grep -qx "${KIND_CLUSTER}"; then
    kind create cluster --name "${KIND_CLUSTER}" --config "${LOCAL_DIR}/kind-cluster.yaml" ${KIND_NODE_IMAGE:+--image "${KIND_NODE_IMAGE}"}
  fi

  prepare_chart

  # Same image as the add-on, pulled from ghcr.io instead of the Marketplace registry.
  export LOCAL_IMAGE_REPO="ghcr.io/splunk/splunk-connect-for-syslog/container3" LOCAL_IMAGE_TAG="${CHART_APPVERSION}"
  if [[ -n "${SC4S_IMAGE:-}" ]]; then
    kind load docker-image "${SC4S_IMAGE}" --name "${KIND_CLUSTER}"
    LOCAL_IMAGE_REPO="${SC4S_IMAGE%:*}"
    LOCAL_IMAGE_TAG="${SC4S_IMAGE##*:}"
  fi
  local local_values="${BUILD_DIR}/local-values.yaml"
  yq -n '.splunk.hec_url = strenv(HEC_URL) | .splunk.hec_verify_tls = strenv(HEC_VERIFY_TLS)
         | .image.repository = strenv(LOCAL_IMAGE_REPO) | .image.tag = strenv(LOCAL_IMAGE_TAG)' > "${local_values}"

  "${K[@]}" create namespace "${NAMESPACE}" --dry-run=client -o yaml | "${K[@]}" apply -f -

  local secret_name secret_key
  secret_name="$(yq e '.splunk.existingSecret // ""' "${SETTINGS_FILE}")"
  if [[ -n "${secret_name}" ]]; then
    secret_key="$(yq e '.splunk.existingSecretKey // "hec_token"' "${SETTINGS_FILE}")"
    printf '%s' "${HEC_TOKEN}" \
      | "${K[@]}" -n "${NAMESPACE}" create secret generic "${secret_name}" --from-file="${secret_key}=/dev/stdin" --dry-run=client -o yaml \
      | "${K[@]}" apply -f -
  else
    export HEC_TOKEN
    yq -i '.splunk.hec_token = strenv(HEC_TOKEN)' "${local_values}"
  fi

  helm template "${RELEASE}" "${EKS_CHART_DIR}" --namespace "${NAMESPACE}" --no-hooks \
    --kube-version "$("${K[@]}" version -o json | jq -r '.serverVersion.gitVersion')" \
    -f "${SETTINGS_FILE}" -f "${local_values}" \
    | "${K[@]}" apply -n "${NAMESPACE}" --server-side --field-manager=eks --force-conflicts -f -

  "${K[@]}" -n "${NAMESPACE}" rollout status "statefulset/${FULLNAME}" --timeout=10m
  status
}

send() {
  local marker pod
  marker="sc4s-eks-addon-local-$(date +%s)"
  pod="sc4s-sender-$(date +%s)"
  "${K[@]}" -n "${NAMESPACE}" run "${pod}" --restart=Never --image=busybox:1.36 \
    --env "MSG=<13>$(date -u '+%b %d %H:%M:%S') sc4s-local-test test: ${marker}" \
    --env "TCP_HOST=${FULLNAME}-tcp" --env "UDP_HOST=${FULLNAME}-udp" \
    --command -- sh -c 'echo "$MSG tcp" | nc -w 2 "$TCP_HOST" 514 && echo "$MSG udp" | nc -u -w 2 "$UDP_HOST" 514 && echo sent'
  "${K[@]}" -n "${NAMESPACE}" wait --for=jsonpath='{.status.phase}'=Succeeded "pod/${pod}" --timeout=90s
  "${K[@]}" -n "${NAMESPACE}" logs "pod/${pod}"
  "${K[@]}" -n "${NAMESPACE}" delete pod "${pod}" --wait=false
  echo "Search Splunk for: index=* \"${marker}\""
}

status() {
  "${K[@]}" -n "${NAMESPACE}" get statefulset,pods,services,pvc -o wide
  "${K[@]}" -n "${NAMESPACE}" logs "${FULLNAME}-0" --tail=20 || true
}

down() {
  kind delete cluster --name "${KIND_CLUSTER}"
}

case "${1:-up}" in
  up | send | status | down) "$1" ;;
  *) echo "Usage: $0 {up|send|status|down}" >&2; exit 1 ;;
esac
