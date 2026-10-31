"""Полная сборка издания: проверки -> docx (проход 1) -> PDF -> замер страниц -> docx (проход 2) -> PDF -> проверка оглавления -> dist/.
Требуется: pandoc, python-docx, LibreOffice (soffice). Переменная SOFFICE задаёт команду конвертации."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, assemble, edition
import check
import docxflow

BUILD = ROOT / "build"
DIST = ROOT / "dist"
SOFFICE = os.environ.get("SOFFICE", "soffice --headless --convert-to pdf --outdir .").split()


def main():
    errors, _ = check.run()
    if errors:
        sys.exit("Сборка остановлена: исправьте ошибки целостности.")
    BUILD.mkdir(exist_ok=True)
    DIST.mkdir(exist_ok=True)
    text, _ = assemble()
    (BUILD / "full.md").write_text(text, encoding="utf-8")
    docx, pdf, n = docxflow.build(BUILD)
    ed = edition()
    ver = ed.get("analytic_edition", ed["edition"])
    shutil.copy(docx, DIST / f"digital-tenge-report-{ver}.docx")
    shutil.copy(pdf, DIST / f"digital-tenge-report-{ver}.pdf")
    print(f"Готово: {n} стр.; файлы в dist/ (аналитическая редакция {ver})")


if __name__ == "__main__":
    main()
