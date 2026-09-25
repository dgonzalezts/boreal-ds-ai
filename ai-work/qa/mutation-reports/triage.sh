#!/usr/bin/env bash
set -uo pipefail

LOG="$1"
PKG="/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-eoa17662/packages/boreal-web-components"
cd "$PKG"

tmp=$(mktemp -d)

awk '
  /^\[(Survived|NoCoverage|Timeout)\]/ {
    tag=$1; gsub(/\[|\]/,"",tag); getline;
    if ($0 ~ /^src\//) { split($0,a,":"); print a[1]"\t"a[2]"\t"tag }
  }
' "$LOG" | sort -u > "$tmp/mutants.tsv"

while IFS=$'\t' read -r file line tag; do
  c=$(git blame -L "$line,$line" --porcelain -- "$file" 2>/dev/null | awk 'NR==1{print substr($1,1,9)}')
  printf '%s\t%s\t%s\t%s\n' "$file" "$line" "$tag" "${c:-?}"
done < "$tmp/mutants.tsv" > "$tmp/joined.tsv"

echo "===== counts by commit ====="
cut -f4 "$tmp/joined.tsv" | sort | uniq -c | sort -rn
echo "===== counts by file + commit ====="
awk -F'\t' '{print $1"  "$4}' "$tmp/joined.tsv" | sort | uniq -c | sort -rn
echo "===== counts by tag ====="
cut -f3 "$tmp/joined.tsv" | sort | uniq -c | sort -rn
echo "===== joined (file line tag commit) ====="
cat "$tmp/joined.tsv"
