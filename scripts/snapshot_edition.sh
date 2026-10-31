#!/usr/bin/env bash
# Фиксирует выпуск: копирует собранные файлы и снимок реестров в editions/<номер>/ и считает SHA256SUMS.
# Публичная редакция -> editions/<public_edition>/ ; аналитическая -> editions/<analytic_edition>/ (если ещё нет).
set -e
cd "$(dirname "$0")/.."
get() { awk -F': ' -v k="$1" '$1==k {sub(/[ \t]+#.*$/,"",$2); gsub(/"/,"",$2); print $2}' edition.yml; }
pub=$(get public_edition); ana=$(get analytic_edition)
snap() { # $1 папка, остальные — файлы
  dir="editions/$1"; shift; mkdir -p "$dir/registry_snapshot"
  for f in "$@"; do [ -e "$f" ] && cp "$f" "$dir"/; done
  cp registry/*.csv watch/indicators.csv "$dir/registry_snapshot/"; cp edition.yml "$dir/"
  ( cd "$dir" && sha256sum $(ls | grep -E '\.(docx|pdf|html|png|json)$') > SHA256SUMS )
  echo "Снимок в $dir"
}
if [ -n "$pub" ] && [ "$pub" = "$ana" ]; then   # общий выпуск обеих дорожек (с 1.1.1)
  snap "$pub" dist/digital-tenge-popsci-"$pub"* dist/digital-tenge-report-"$ana".*
  exit 0
fi
[ -n "$pub" ] && ls dist/digital-tenge-popsci-* >/dev/null 2>&1 && snap "$pub" dist/digital-tenge-popsci-"$pub"*
if [ -n "$ana" ] && [ ! -d "editions/$ana" ]; then snap "$ana" dist/digital-tenge-report-"$ana".*; fi
