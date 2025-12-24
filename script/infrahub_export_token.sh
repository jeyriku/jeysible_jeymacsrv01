#!/usr/bin/env bash
# Usage: eval "$(script/infrahub_export_token.sh /path/to/vault_pass username)"
# Ex: eval "$(script/infrahub_export_token.sh /tmp/.vault_pass jeyriku)"

set -euo pipefail
VAULT_PASS_FILE=${1:-}
USER=${2:-jeyriku}

if [ -z "${VAULT_PASS_FILE}" ]; then
  echo "Usage: $0 /path/to/vault_password_file username" >&2
  exit 2
fi

if ! command -v ansible-vault >/dev/null 2>&1; then
  echo "ansible-vault not found in PATH" >&2
  exit 2
fi

TOKEN=$(ansible-vault view group_vars/all/infrahub_vault.yml --vault-password-file "${VAULT_PASS_FILE}" 2>/dev/null | \
  python3 -c "import sys,yaml; d=yaml.safe_load(sys.stdin); print(d.get('infrahub_api_tokens',{}).get('${USER}',''))")

if [ -z "${TOKEN}" ]; then
  echo "" # print nothing if empty
  exit 0
fi

printf 'export INFRAHUB_API_TOKEN=%q' "${TOKEN}"
