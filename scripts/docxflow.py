"""Двухпроходная сборка docx и PDF из full.md в каталоге сборки (оглавление с проверкой номеров страниц)."""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

SOFFICE = os.environ.get("SOFFICE", "soffice --headless --convert-to pdf --outdir .").split()
BUILDER = str(Path(__file__).with_name("docx_build.py"))


def _sh(cmd, cwd, env=None):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)


def _texts(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    return n, {p: re.sub(r"[\s\-]+", "", subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True).stdout) for p in range(1, n + 1)}


def build(build_dir, extra_env=None):
    """В build_dir должен лежать full.md (и рисунки по относительным путям). Возвращает (docx, pdf, число страниц)."""
    build_dir = Path(build_dir)
    env = dict(os.environ); env.update(extra_env or {})
    _sh([sys.executable, BUILDER, "1", str(build_dir)], build_dir, env)
    _sh(SOFFICE + ["pass1.docx"], build_dir, env)
    ents = json.load(open(build_dir / "toc_entries.json"))
    n, txt = _texts(str(build_dir / "pass1.pdf"))
    pg, cur = [], 3
    for lvl, h in ents:
        key = re.sub(r"[\s\-]+", "", h)[:34]
        f = next((p for p in range(cur, n + 1) if key in txt[p]), None)
        if f is None:
            print("Заголовок не найден в PDF:", h); f = cur
        pg.append(f); cur = f
    json.dump(pg, open(build_dir / "toc_pages.json", "w"))
    _sh([sys.executable, BUILDER, "2", str(build_dir)], build_dir, env)
    _sh(SOFFICE + ["final.docx"], build_dir, env)
    n, txt = _texts(str(build_dir / "final.pdf"))
    bad = [h for (l, h), p in zip(ents, pg) if p not in [q for q in range(3, n + 1) if re.sub(r"[\s\-]+", "", h)[:34] in txt[q]]]
    if bad:
        sys.exit(f"Оглавление не совпало с вёрсткой: {bad}")
    return build_dir / "final.docx", build_dir / "final.pdf", n
