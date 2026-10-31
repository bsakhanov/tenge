"""Общие функции: чтение настроек издания, реестров, подстановка значений."""
import csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "report" / "src"
REG = ROOT / "registry"
ORDER = ["front", "vol1", "vol2", "vol3", "vol4", "vol5", "vol6", "appendix"]


def edition():
    cfg = {}
    for line in (ROOT / "edition.yml").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#") and ":" in line:
            k, v = line.split(":", 1)
            v = re.sub(r"\s+#.*$", "", v.strip())
            cfg[k.strip()] = v.strip().strip('"')
    return cfg


def read_csv(name):
    with open(REG / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def md_table(rows, cols, headers):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(r[c].replace("|", "/").replace("\n", " ") for c in cols) + " |")
    return "\n".join(out)


def ai_counts(text):
    """Подсчёт вердиктов таблицы проверки черновика ИИ (часть «Проверка черновика ИИ»)."""
    i = text.find("**Таблица 15.1")
    cnt = {"Подтверждено": 0, "Подтверждено частично": 0, "Не подтверждено": 0, "Опровергнуто первоисточником": 0}
    n = 0
    if i < 0:
        return n, cnt
    for l in text[i:].split("\n"):
        if re.match(r"\| \d+ \|", l):
            n += 1
            v = l.split("|")[3].strip()
            cnt[v] = cnt.get(v, 0) + 1
    return n, cnt


def vkey(s):
    return tuple(int(x) for x in str(s).split(".") if x.isdigit())


def facts_for_analytic():
    """Факты, существовавшие на момент аналитической редакции: добавленные позже в неё не входят,
    а замены, сделанные позже, не применяются (факт остаётся действующим)."""
    ed = edition(); cap = vkey(ed.get("analytic_edition", ed["edition"]))
    allf = read_csv("facts.csv"); by = {r["id"]: r for r in allf}
    out = []
    for r in allf:
        if vkey(r.get("added_in", "1.0")) > cap:
            continue
        r = dict(r)
        sup = by.get(r.get("superseded_by", ""))
        if r.get("status") == "superseded" and sup and vkey(sup.get("added_in", "1.0")) > cap:
            r["status"] = "verified"; r["superseded_by"] = ""
        out.append(r)
    return out


def assemble():
    """Склеивает исходники, подставляет таблицы реестров и значения плейсхолдеров."""
    ed = edition()
    parts = [(SRC / f"{n}.md").read_text(encoding="utf-8") for n in ORDER]
    text = "\n\n".join(parts)
    facts, disc, gaps = facts_for_analytic(), read_csv("discrepancies.csv"), read_csv("gaps.csv")
    def fact_row(r):
        content = r["content"]
        if r.get("status") == "superseded":
            content = f"(устарел; заменён: {r.get('superseded_by', '')}) " + content
        return "| " + " | ".join(x.replace("|", "/") for x in (r["id"], content, r["source"], r["year"])) + " |"
    text = text.replace("<!-- TABLE:facts -->", "| Код | Содержание | Источник | Год данных |\n|---|---|---|---|\n" + "\n".join(fact_row(r) for r in facts))
    text = text.replace("<!-- TABLE:discrepancies -->", md_table(disc, ["id", "description", "status"], ["Код", "Расхождение", "Статус"]))
    text = text.replace("<!-- TABLE:gaps -->", md_table(gaps, ["id", "question", "status"], ["Код", "Вопрос, на который материалы ответа не дают", "Статус"]))
    n_ai, c = ai_counts(text)
    subs = {
        "EDITION": ed.get("analytic_edition", ed["edition"]), "DATE": ed["date_text"],
        "N_FACTS": str(len(facts)), "N_DISC": str(len(disc)), "N_GAPS": str(sum(1 for g in gaps if not g["status"].startswith("закрыто"))),
        "N_AI": str(n_ai), "AI_OK": str(c["Подтверждено"]), "AI_PART": str(c["Подтверждено частично"]),
        "AI_NO": str(c["Не подтверждено"]), "AI_REF": str(c["Опровергнуто первоисточником"]),
    }
    for k, v in subs.items():
        text = text.replace("{{" + k + "}}", v)
    return text, subs
