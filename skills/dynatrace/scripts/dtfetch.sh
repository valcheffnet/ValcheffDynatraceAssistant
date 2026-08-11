#!/usr/bin/env bash
# Harvest docs.dynatrace.com pages as clean text.
# Usage: ./dtfetch.sh <doc-path> [<doc-path> ...]
#   doc-path is relative to https://docs.dynatrace.com/docs/
# Output: cache/<slugified-path>.txt
set -uo pipefail
CACHE="$(dirname "$0")/cache"
mkdir -p "$CACHE"
for p in "$@"; do
  slug="${p//\//__}"
  out="$CACHE/$slug.txt"
  if [[ -s "$out" ]]; then echo "cached  $p"; continue; fi
  html=$(mktemp --suffix=.html)
  if curl -sSf --max-time 45 "https://docs.dynatrace.com/docs/$p" -o "$html"; then
    # strip chrome: drop leading nav lines and trailing footer boilerplate
    lynx -dump -nolist -width=110 "$html" 2>/dev/null \
      | sed '1,8{/IFRAME\|(BUTTON)\|Documentation$\|Search documentation\|Try it free\|^ *Login/d}' \
      | sed -n '1,/^ *Related tags$/p' \
      > "$out"
    printf 'ok      %-70s %s lines\n' "$p" "$(wc -l < "$out")"
  else
    echo "FAIL    $p"
  fi
  rm -f "$html"
done
