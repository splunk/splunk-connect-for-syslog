#!/bin/bash
# Builds the EKS add-on chart and checks it against EKS add-on constraints.
# Override the Kubernetes versions with K8S_VERSIONS="1.33 1.34".
set -euo pipefail

source "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/common.sh"

read -r -a K8S_VERSIONS <<< "${K8S_VERSIONS:-1.30 1.31 1.32 1.33 1.34 1.35}"
SAMPLE_SETTINGS="${EKS_ADDON_DIR}/settings.example.yaml"
failures=0

pass() { echo "ok    $*"; }
fail() { echo "FAIL  $*"; failures=$((failures + 1)); }

# Hooks and CRDs stay in the output (no --no-hooks, plus --include-crds), because the
# checks below look for them; EKS add-ons may contain neither.
render() {
  helm template splunk-connect-for-syslog "${EKS_CHART_DIR}" --namespace sc4s --include-crds "$@"
}

prepare_chart

if helm lint "${EKS_CHART_DIR}" > /dev/null; then pass "helm lint"; else fail "helm lint"; fi

for v in "${K8S_VERSIONS[@]}"; do
  if render --kube-version "${v}" > /dev/null; then pass "renders on Kubernetes ${v}"; else fail "renders on Kubernetes ${v}"; fi
done

if jq empty "${EKS_CHART_DIR}/aws_mp_configuration_schema.json"; then
  pass "aws_mp_configuration_schema.json is valid JSON"
else
  fail "aws_mp_configuration_schema.json is missing or invalid"
fi

MP_SCHEMA="${EKS_CHART_DIR}/aws_mp_configuration_schema.json"
schema_uri="$(jq -r '."$schema" // ""' "${MP_SCHEMA}")"
case "${schema_uri}" in
  https://json-schema.org/draft-04/schema | https://json-schema.org/draft-06/schema | \
  https://json-schema.org/draft-07/schema | https://json-schema.org/draft/2019-09/schema)
    pass "\$schema is supported by EKS add-ons" ;;
  *) fail "\$schema '${schema_uri}' is not one EKS add-ons support" ;;
esac

undescribed="$(jq -r '[paths(type == "object") as $p | select($p[-2] == "properties") | select((getpath($p).description // "") == "") | $p | map(select(. != "properties" and . != "items")) | join(".")] | join(" ")' "${MP_SCHEMA}")"
if [[ -z "${undescribed}" ]]; then pass "every add-on setting has a description"; else fail "add-on settings without a description: ${undescribed}"; fi

if cmp -s "${EKS_CHART_DIR}/values.schema.json" "${MP_SCHEMA}"; then
  pass "chart validates with the add-on schema"
else
  fail "values.schema.json differs from aws_mp_configuration_schema.json"
fi

if rendered="$(render -f "${SAMPLE_SETTINGS}")" && [[ -n "${rendered}" ]]; then
  pass "sample settings pass the add-on schema"
else
  fail "sample settings rejected"
  rendered=""
fi

# Add-on settings must be camelCase; the chart's older snake_case names are refused.
if render --set splunk.hec_url=https://x:8088 > /dev/null 2>&1 || render --set-json 'sc4s.vendor_product=[]' > /dev/null 2>&1; then
  fail "add-on schema accepts old snake_case setting names"
else
  pass "add-on schema rejects old snake_case setting names"
fi
non_camel="$(jq -r '[paths | select(.[-2] == "properties") | .[-1]] | unique | .[] | select(test("^[a-z][a-zA-Z0-9]*$") | not)' "${EKS_CHART_DIR}/aws_mp_configuration_schema.json")"
if [[ -z "${non_camel}" ]]; then pass "all add-on setting names are camelCase"; else fail "add-on setting names not camelCase: $(echo ${non_camel})"; fi

# Add-on settings must not accept secrets (AWS INVALID_HELM_SENSITIVE_CONFIG).
if render --set splunk.hec_token=x > /dev/null 2>&1; then fail "add-on schema accepts splunk.hec_token"; else pass "add-on schema rejects splunk.hec_token"; fi
if render --set env.SC4S_DEST_SPLUNK_HEC_OTHER_TOKEN=x > /dev/null 2>&1; then
  fail "add-on schema accepts a credential in env"
else
  pass "add-on schema rejects credential env names"
fi

if [[ "$(yq e '(.dependencies // []) | length' "${EKS_CHART_DIR}/Chart.yaml")" == "0" && ! -d "${EKS_CHART_DIR}/charts" ]]; then
  pass "no subchart dependencies"
else
  fail "chart has subchart dependencies"
fi

if grep -rqE '\blookup\b' "${EKS_CHART_DIR}/templates"; then fail "templates use lookup"; else pass "no lookup calls"; fi

if [[ -z "${rendered}" ]]; then
  fail "hook, CRD and image checks not run: the sample settings did not render"
else
  if grep -q 'helm.sh/hook' <<< "${rendered}"; then fail "chart contains Helm hooks"; else pass "no Helm hooks"; fi

  if grep -q '^kind: CustomResourceDefinition' <<< "${rendered}"; then fail "chart contains CRDs"; else pass "no CRDs"; fi

  requests="$(yq e -N 'select(.kind == "DaemonSet" or .kind == "Deployment") | .spec.template.spec.containers[0].resources.requests | (.cpu // "") + " " + (.memory // "")' - <<< "${rendered}" | xargs)"
  if [[ "${requests}" =~ ^[^\ ]+\ [^\ ]+$ ]]; then pass "default resource requests: cpu ${requests% *}, memory ${requests#* }"; else fail "no default CPU and memory requests"; fi

  if grep -qE '^kind: (Deployment|DaemonSet)$' <<< "${rendered}"; then
    pass "contains a Deployment or DaemonSet"
  else
    fail "no Deployment or DaemonSet, which EKS needs to track the add-on"
  fi

  images="$(grep -E '^\s+image:' <<< "${rendered}" | awk '{print $2}' | tr -d '"' || true)"
  bad_images="$(grep -v "^${ECR_REGISTRY}/" <<< "${images}" || true)"
  if [[ -z "${images}" ]]; then
    fail "no images found in the render"
  elif [[ -n "${bad_images}" ]]; then
    fail "images outside the Marketplace registry: ${bad_images}"
  else
    pass "all images come from ${ECR_REGISTRY}"
  fi
fi

if [[ "${failures}" -gt 0 ]]; then
  echo "${failures} check(s) failed"
  exit 1
fi
echo "All checks passed"
