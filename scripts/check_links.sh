#!/bin/bash
# Overí, že každý [text](*.md) odkaz smeruje na existujúci súbor.
set -u
fail=0
for src in *.md appendices/*.md; do
  dir=$(dirname "$src")
  while IFS= read -r target; do
    [ -z "$target" ] && continue
    if [ ! -f "$dir/$target" ] && [ ! -f "$target" ]; then
      echo "BROKEN: $src -> $target"; fail=1
    fi
  done < <(grep -oE '\]\([^)#]+\.md' "$src" | sed 's/](\(.*\)/\1/')
done
exit $fail
