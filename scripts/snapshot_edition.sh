#!/usr/bin/env bash
# Фиксирует выпуск: копирует dist/ и снимок реестров в editions/<редакция>/, считает SHA256SUMS.
set -e
cd "$(dirname "$0")/.."
ed=$(awk -F': ' '/^edition:/{gsub(/"/,"",$2); print $2}' edition.yml)
dir="editions/$ed"; mkdir -p "$dir/registry_snapshot"
cp dist/*.docx dist/*.pdf "$dir"/
cp registry/*.csv "$dir/registry_snapshot/"
cp watch/indicators.csv "$dir/registry_snapshot/"
cp edition.yml "$dir/"
( cd "$dir" && sha256sum *.docx *.pdf > SHA256SUMS )
echo "Снимок в $dir"
