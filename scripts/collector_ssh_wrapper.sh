#!/usr/bin/env bash
set -euo pipefail
# collector_ssh_wrapper.sh <host> <user> <pass>
host="$1"
user="$2"
pass="$3"
out="./show_version_${host}_linux.txt"
tmp=$(mktemp)
rc=0

# Try sshpass first (force a tty with -tt for devices that require pty)
if command -v sshpass >/dev/null 2>&1; then
  sshpass -p "$pass" ssh -tt -o PreferredAuthentications=password,keyboard-interactive -oPubkeyAuthentication=no \
    -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oConnectTimeout=10 -l "$user" "$host" \
    'uname -a; echo "---OS-RELEASE---"; cat /etc/os-release 2>/dev/null || true' > "$tmp" 2>&1 || rc=$?
else
  rc=127
fi

if [ -s "$tmp" ] && [ "$rc" -eq 0 ]; then
  # If the target answered with network-CLI style errors, treat as failure so Expect fallback runs
  if grep -qE "(Unknown command|% Unrecognized command|Unrecognized command)" "$tmp"; then
    rc=2
  else
    mv "$tmp" "$out"
    exit 0
  fi
fi

# Fallback to expect script (prefer repository-level script)
EXPECT_SCRIPT="/Users/jeremierouzet/Documents/Dev/ansible/jeysible_jeymacsrv01/scripts/collect_via_expect.exp"
if command -v expect >/dev/null 2>&1 && [ -f "$EXPECT_SCRIPT" ]; then
  /usr/bin/env expect "$EXPECT_SCRIPT" "$host" "$user" "$pass" > "$tmp" 2>&1 || rc=$?
  if [ -s "$tmp" ] && [ "$rc" -eq 0 ]; then
    mv "$tmp" "$out"
    exit 0
  fi
fi

# Last-resort: move whatever we captured for debugging
mv "$tmp" "$out" || true
exit 2
