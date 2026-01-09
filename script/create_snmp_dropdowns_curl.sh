#!/usr/bin/env bash
set -euo pipefail

# Script fallback pour créer les dropdowns SNMP via curl si le SDK Python ne peut atteindre l'API.
# Usage: export INFRAHUB_API_TOKEN=... ; export INFRAHUB_ADDRESS=http://192.168.0.237:8000 ; bash script/create_snmp_dropdowns_curl.sh

ENDPOINT="${INFRAHUB_ADDRESS:-http://192.168.0.237:8000}"
TOKEN="${INFRAHUB_API_TOKEN:-${INFRAHUB_TOKEN:-}}"

if [ -z "$TOKEN" ]; then
  echo "ERROR: INFRAHUB_API_TOKEN non défini"
  exit 2
fi

SAMPLE_NAMES=(
  "snmp_location"
  "snmp_community"
  "snmp_server1"
  "snmp_server2"
  "snmp_server3"
  "snmp_server4"
)

SAMPLE_VALUES=(
  "int.jeyriku.net, 2 allee des campagnols, Seynod, 74600, Annecy, France [45.85995, 6.0793]"
  "jeyricorp"
  "192.168.0.239"
  "192.168.0.248"
  "192.168.0.249"
  "192.168.0.251"
)

MUTATION='mutation SchemaDropdownAdd($data: SchemaDropdownAddInput!) { SchemaDropdownAdd(data: $data) { ok object { value label description } } }'

for i in "${!SAMPLE_NAMES[@]}"; do
  name="${SAMPLE_NAMES[$i]}"
  val="${SAMPLE_VALUES[$i]}"
  echo "--- Creating dropdown: $name -> $val"
  payload=$(python3 -c 'import json,sys
name=sys.argv[1]
val=sys.argv[2]
mut=sys.argv[3]
data={"attribute":name,"dropdown":name,"kind":"profile","label":name,"values":[val]}
print(json.dumps({"query":mut,"variables":{"data":data}}))' "$name" "$val" "$MUTATION")

  curl -sS -X POST "$ENDPOINT/graphql" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-INFRAHUB-KEY: $TOKEN" \
    -d "$payload" | jq '.' || true
  echo
done

echo "Done. Vérifiez les réponses ci-dessus pour chaque dropdown."
