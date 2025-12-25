#!/usr/bin/env bash
# Robust attach script for Infrahub ProfileDcimDeviceUpsert
# Features: resume, batching, retries, timeouts, cleanup, detailed logging
# Usage: TOKEN=... ENDPOINT=... PROFILE_ID=... ./attach_snmp_profile_upsert.sh devices.txt

set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: TOKEN=... ENDPOINT=... PROFILE_ID=... $0 devices_file" >&2
  exit 2
fi
DEV_FILE="$1"
# Allow using either TOKEN or INFRAHUB_API_TOKEN (convenience for local runs)
TOKEN=${TOKEN:-${INFRAHUB_API_TOKEN:-}}
if [ -z "$TOKEN" ]; then
  echo "Environment variable TOKEN or INFRAHUB_API_TOKEN required (use Authorization: Bearer <token>)" >&2
  exit 2
fi

# ENDPOINT fallback to common Infrahub address if not provided
ENDPOINT=${ENDPOINT:-${INFRAHUB_ENDPOINT:-http://192.168.0.237:8000/graphql}}

: "${PROFILE_ID:?Environment variable PROFILE_ID required (existing SNMP profile id)}"

# Configurable parameters (can be exported before running)
BATCH_SIZE=${BATCH_SIZE:-10}
SLEEP_BETWEEN=${SLEEP_BETWEEN:-0.2}
CONNECT_TIMEOUT=${CONNECT_TIMEOUT:-5}
MAX_TIME=${MAX_TIME:-30}
CURL_RETRIES=${CURL_RETRIES:-2}
CURL_RETRY_DELAY=${CURL_RETRY_DELAY:-2}
ATTACH_RESULTS_FILE=${ATTACH_RESULTS_FILE:-attach_loop_results.txt}
LOG_PREFIX=${LOG_PREFIX:-attach_debug}

# ensure jq and curl available
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 3; }
command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 3; }

# prepare logging
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
DEBUG_LOG="${LOG_PREFIX}_${TIMESTAMP}.log"
: > "$DEBUG_LOG"
exec 3>&1 4>&2
# tee stdout/stderr into debug log
# All echo statements will still go to stdout/stderr; we append key debug info to $DEBUG_LOG where useful

# helper to append both to stdout and debug log
log() { printf "%s\n" "$@" | tee -a "$DEBUG_LOG" >&3; }
logerr() { printf "%s\n" "$@" | tee -a "$DEBUG_LOG" >&4; }

# Build set of already-processed device IDs to resume
touch "$ATTACH_RESULTS_FILE"
awk '/^\[OK\]/{print $2} /^\[FAIL\]/{print $2} /^\[ERROR\]/{print $2}' "$ATTACH_RESULTS_FILE" | sort -u > .processed_ids.tmp || true

# Read devices into array, filter out processed (portable alternative to mapfile)
remaining_devices=()
while IFS= read -r line || [ -n "$line" ]; do
  # strip CR and skip empty lines
  d=$(printf "%s" "$line" | sed -e 's/\r$//')
  [ -z "$d" ] && continue
  if grep -qxF "$d" .processed_ids.tmp; then
    log "[SKIP] $d (already processed)"
    continue
  fi
  remaining_devices+=("$d")
done < "$DEV_FILE"

total=${#remaining_devices[@]}
log "Starting attach run: ${total} devices to process (batch=${BATCH_SIZE})"

cleanup() {
  rm -f .processed_ids.tmp
}
trap cleanup EXIT

# function to process single device with retries
process_device() {
  local device_id="$1"
  local tries=0
  local ok=false
  local last_body=""
  while [ $tries -le $CURL_RETRIES ]; do
    tries=$((tries+1))
    payload_file=$(mktemp /tmp/infrahub_payload.XXXXXX.json)
    jq -n --arg m "$MUTATION" --arg pid "$PROFILE_ID" --arg did "$device_id" '{query:$m, variables: {data:{id:$pid, profile_name:{value:"SNMP"}, related_nodes:[{id:$did, kind:"DcimDevice"}]}}}' > "$payload_file"

    resp=$(curl -s -w "\n%{http_code}" \
      --connect-timeout "$CONNECT_TIMEOUT" --max-time "$MAX_TIME" \
      -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -H "X-INFRAHUB-KEY: $TOKEN" \
      -H "Authorization: Bearer $TOKEN" \
      --data-binary "@$payload_file") || true
    rm -f "$payload_file"

    http_code=$(printf "%s" "$resp" | tail -n1)
    body=$(printf "%s" "$resp" | sed '$d')
    last_body="$body"

    if [ "$http_code" = "200" ]; then
      ok=$(printf "%s" "$body" | jq -r '.data.ProfileDcimDeviceUpsert.ok // false' 2>/dev/null || echo false)
      if [ "$ok" = "true" ]; then
        echo "[OK] $device_id" >> "$ATTACH_RESULTS_FILE"
        log "[OK] $device_id"
        return 0
      else
        # server returned 200 but ok:false
        echo "[FAIL] $device_id" >> "$ATTACH_RESULTS_FILE"
        printf "%s\n" "$body" >> "$ATTACH_RESULTS_FILE"
        logerr "[FAIL] $device_id -- server returned ok:false; body: $body"
        return 2
      fi
    else
      logerr "Attempt $tries: HTTP $http_code for device $device_id; body: $body"
      if [ $tries -le $CURL_RETRIES ]; then
        sleep $CURL_RETRY_DELAY
        continue
      else
        echo "[ERROR] HTTP $http_code for device $device_id" >> "$ATTACH_RESULTS_FILE"
        printf "%s\n" "$body" >> "$ATTACH_RESULTS_FILE"
        return 3
      fi
    fi
  done
  # should not reach here
  echo "[ERROR] Unknown failure for $device_id" >> "$ATTACH_RESULTS_FILE"
  printf "%s\n" "$last_body" >> "$ATTACH_RESULTS_FILE"
  return 4
}

# ensure MUTATION var available (keep the GraphQL definition)
read -r -d '' MUTATION <<'GQL' || true
mutation ProfileDcimDeviceUpsert($data: ProfileDcimDeviceUpsertInput!) {
  ProfileDcimDeviceUpsert(data: $data) {
    ok
    object { id profile_name { value } }
  }
}
GQL

# process in batches
i=0
while [ $i -lt ${#remaining_devices[@]} ]; do
  batch_end=$((i + BATCH_SIZE - 1))
  [ $batch_end -ge ${#remaining_devices[@]} ] && batch_end=$((${#remaining_devices[@]} - 1))
  log "Processing batch $((i / BATCH_SIZE + 1)): devices $((i+1))..$((batch_end+1))"
  for idx in $(seq $i $batch_end); do
    dev=${remaining_devices[$idx]}
    process_device "$dev" || true
    sleep "$SLEEP_BETWEEN"
  done
  i=$((batch_end + 1))
  # small pause between batches
  sleep 0.5
done

log "Attach run complete. Results:"
wc -l "$ATTACH_RESULTS_FILE" | tee -a "$DEBUG_LOG"
log "Debug log: $DEBUG_LOG"

exit 0
