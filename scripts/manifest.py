"""Обновление sources/manifest.csv по файлам в sources/files/ (хэш, размер, страницы). Роль и дату заполнять вручную."""
import csv, hashlib, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
F = ROOT / "sources" / "files"
M = ROOT / "sources" / "manifest.csv"
old = {r["file"]: r for r in csv.DictReader(open(M, encoding="utf-8"))} if M.exists() else {}
rows = []
for p in sorted(F.glob("*")):
    if not p.is_file(): continue
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    pages = ""
    if p.suffix.lower() == ".pdf":
        m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True).stdout)
        pages = m.group(1) if m else ""
    o = old.get(p.name, {})
    rows.append([p.name, o.get("role", ""), o.get("doc_date", ""), pages, p.stat().st_size, h, o.get("first_used_in", "")])
for name, o in old.items():
    if name not in {r[0] for r in rows}:
        rows.append([name, o["role"], o["doc_date"], o["pages"], o["size_bytes"], o["sha256"], o["first_used_in"]])
with open(M, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["file", "role", "doc_date", "pages", "size_bytes", "sha256", "first_used_in"]); w.writerows(rows)
print(len(rows), "записей в манифесте")
