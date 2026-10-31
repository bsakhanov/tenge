"""Полная сборка издания: проверки -> docx (проход 1) -> PDF -> замер страниц -> docx (проход 2) -> PDF -> проверка оглавления -> dist/.
Требуется: pandoc, python-docx, LibreOffice (soffice). Переменная SOFFICE задаёт команду конвертации."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, assemble, edition
import check

BUILD = ROOT / "build"
DIST = ROOT / "dist"
SOFFICE = os.environ.get("SOFFICE", "soffice --headless --convert-to pdf --outdir .").split()


def sh(cmd, cwd=BUILD):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pages(pdf):
    return int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))


def page_texts(pdf):
    n = pages(pdf)
    return n, {p: re.sub(r"[\s\-]+", "", subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True).stdout) for p in range(1, n + 1)}


def main():
    errors, _ = check.run()
    if errors:
        sys.exit("Сборка остановлена: исправьте ошибки целостности.")
    BUILD.mkdir(exist_ok=True)
    DIST.mkdir(exist_ok=True)
    text, _ = assemble()
    (BUILD / "full.md").write_text(text, encoding="utf-8")
    builder = str(ROOT / "scripts" / "docx_build.py")
    sh([sys.executable, builder, "1", str(BUILD)])
    sh(SOFFICE + ["pass1.docx"])
    ents = json.load(open(BUILD / "toc_entries.json"))
    n, txt = page_texts(str(BUILD / "pass1.pdf"))
    pg, cur = [], 3
    for lvl, h in ents:
        key = re.sub(r"[\s\-]+", "", h)[:34]
        f = next((p for p in range(cur, n + 1) if key in txt[p]), None)
        if f is None:
            print("Заголовок не найден в PDF:", h); f = cur
        pg.append(f); cur = f
    json.dump(pg, open(BUILD / "toc_pages.json", "w"))
    sh([sys.executable, builder, "2", str(BUILD)])
    sh(SOFFICE + ["final.docx"])
    n, txt = page_texts(str(BUILD / "final.pdf"))
    bad = [h for (l, h), p in zip(ents, pg) if p not in [q for q in range(3, n + 1) if re.sub(r"[\s\-]+", "", h)[:34] in txt[q]]]
    if bad:
        sys.exit(f"Оглавление не совпало с вёрсткой: {bad}")
    ed = edition()["edition"]
    shutil.copy(BUILD / "final.docx", DIST / f"digital-tenge-report-{ed}.docx")
    shutil.copy(BUILD / "final.pdf", DIST / f"digital-tenge-report-{ed}.pdf")
    print(f"Готово: {n} стр.; файлы в dist/ (редакция {edition()['edition']})")


if __name__ == "__main__":
    main()
