#!/usr/bin/env bash
# Извлечение текста из sources/files/*: PDF с текстовым слоем -> pdftotext; сканы -> tesseract (rus+eng); docx/pptx -> pandoc/extract-text.
set -e
cd "$(dirname "$0")/.."
mkdir -p sources/text
for f in sources/files/*; do
  b=$(basename "$f"); n="${b%.*}"
  case "${f##*.}" in
    pdf)
      fonts=$(pdffonts "$f" 2>/dev/null | tail -n +3 | wc -l)
      if [ "$fonts" -gt 0 ]; then
        pdftotext "$f" "sources/text/$n.txt"
      else
        echo "Скан (OCR): $b"
        tmp=$(mktemp -d); pages=$(pdfinfo "$f" | awk '/Pages/{print $2}')
        for p in $(seq 1 "$pages"); do
          pdftoppm -r 130 -f "$p" -l "$p" -gray -png "$f" "$tmp/pg"
          tesseract "$tmp"/pg-*.png "$tmp/page_$(printf %03d "$p")" -l rus+eng --psm 3 >/dev/null 2>&1
          rm -f "$tmp"/pg-*.png
        done
        cat "$tmp"/page_*.txt > "sources/text/$n.txt"; rm -rf "$tmp"
      fi ;;
    docx|pptx|odt) pandoc "$f" -t plain -o "sources/text/$n.txt" ;;
    md|txt) cp "$f" "sources/text/$n.txt" ;;
  esac
done
echo "Готово: sources/text/"
