# Источники

В git лежит только манифест `manifest.csv` (имя файла, роль, дата, число страниц, размер, SHA-256). Сами файлы кладутся в `sources/files/` (в `.gitignore`: размеры до 95 МБ, права третьих лиц), извлечённый текст — в `sources/text/` (тоже вне git).

Обновление манифеста: `python scripts/manifest.py`. Извлечение текста и распознавание сканов: `scripts/extract_sources.sh`.

Для распознавания русского текста нужен tesseract с языком `rus`: `sudo apt install tesseract-ocr tesseract-ocr-rus`.
