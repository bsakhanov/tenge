"""Сборка публичной (научно-популярной) редакции для the-tenge.kz: HTML, docx, PDF и метаданные для Joomla.
Источник правды: report/public/chapters/*.md, report/public/data/*.json, registry/facts.csv (поле public=yes).
Запуск: python scripts/build_public.py"""
import base64, csv, io, json, re, shutil, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, edition
import docxflow

PUB = ROOT / "report" / "public"
BUILD = ROOT / "build" / "public"
DIST = ROOT / "dist"
FACT_RE = re.compile(r"Ф-\d+")


def load_json(n):
    return json.load(open(PUB / "data" / n, encoding="utf-8"))


def read_chapters():
    return [(p.name, p.read_text(encoding="utf-8")) for p in sorted((PUB / "chapters").glob("*.md"))]


def facts_table():
    return {r["id"]: r for r in csv.DictReader(open(ROOT / "registry" / "facts.csv", encoding="utf-8"))}


def gate(chapters, data_blobs):
    """Публичный текст может ссылаться только на опубликованные (public=yes) подтверждённые факты."""
    F = facts_table(); errs = []; used = set()
    for name, t in chapters:
        for m in re.finditer(r"\[\[(Ф-\d+)\]\]", t):
            used.add(m.group(1))
    for blob in data_blobs:
        used |= set(FACT_RE.findall(json.dumps(blob, ensure_ascii=False)))
    for i in sorted(used):
        r = F.get(i)
        if not r: errs.append(f"{i}: нет в реестре")
        elif r["public"] != "yes": errs.append(f"{i}: public=no (сомнительный или внутренний факт)")
        elif r["status"] != "verified": errs.append(f"{i}: статус {r['status']}")
    # числа без ссылок: предупреждение о крупных числах с единицами
    warns = []
    for name, t in chapters:
        for para in re.split(r"\n\s*\n", t):
            if re.search(r"\d[\d\s,]*\s*(млрд|трлн|млн)", para) and "[[Ф-" not in para and not para.startswith("|") and "расчёт" not in para and "условн" not in para:
                warns.append(f"{name}: число с единицей без ссылки на факт: {para[:70]}…")
    return used, errs, warns


def typo_check(chapters):
    bad = []
    for name, t in chapters:
        if re.search(r'(?<![=\w])"[^"\n]+"(?!\})', re.sub(r"\{[^}]*\}", "", t)): bad.append(f"{name}: прямые кавычки")
        if re.search(r"(?<=\S) - (?=\S)", t): bad.append(f"{name}: дефис вместо тире")
        if re.search(r"\bявля(ется|ются)\b", t): bad.append(f"{name}: «является»")
        if re.search(r"(?m)(^|[.!?]\s)\d", re.sub(r"\[\[[^\]]*\]\]", "", t)) and False: pass
    return bad


# ---------------- HTML ----------------
def md_to_html_fragment(md):
    md = re.sub(r"\[\[(Ф-\d+)\]\]", lambda m: f'<span class="fact" data-f="{m.group(1)}">{m.group(1)}</span>', md)
    md = re.sub(r"(?m)^\{\{widget:([\w-]+)\}\}\s*$", lambda m: f'\n<div class="widget" data-widget="{m.group(1)}"></div>\n', md)
    r = subprocess.run(["pandoc", "-f", "markdown+raw_html", "-t", "html5", "--section-divs", "--wrap=none", "--no-highlight"],
                       input=md, capture_output=True, text=True, check=True)
    return r.stdout


def cover_b64():
    from PIL import Image
    im = Image.open(PUB / "figures" / "cover.png").convert("RGB")
    b = io.BytesIO(); im.save(b, "JPEG", quality=84, optimize=True)
    return base64.b64encode(b.getvalue()).decode()


def sources_li():
    lines = [l.strip() for l in (PUB / "sources.md").read_text(encoding="utf-8").splitlines() if l.strip()]
    esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    def link(s):
        s = esc(s)
        return re.sub(r"(https?://[^\s;)]+)", r'<a href="\1" rel="noopener">\1</a>', s)
    return "".join(f"<li>{link(l)}</li>" for l in lines), len(lines)


def build_html(chapters, used, ed):
    F = facts_table()
    facts = [dict(id=i, text=F[i]["content"], source=F[i]["source"], year=F[i]["year"], level=F[i]["level"]) for i in sorted(used)]
    data = dict(facts=facts, glossary=load_json("glossary.json"), faq=load_json("faq.json"), timeline=load_json("timeline.json"),
                countries=load_json("countries.json"), risks=load_json("risks.json"), versions=load_json("versions.json"),
                forms=load_json("forms.json"), lifecycle=load_json("lifecycle.json"))
    body = "".join(md_to_html_fragment(t) for _, t in chapters)
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    read = max(1, round(words / 190))
    tpl = (PUB / "template" / "public.html").read_text(encoding="utf-8")
    css = (PUB / "template" / "style.css").read_text(encoding="utf-8")
    js = (PUB / "template" / "app.js").read_text(encoding="utf-8")
    ver = ed["public_edition"]; author = ed["author_public"]
    title = "Третья форма тенге: как Казахстан учит деньги выполнять условия"
    desc = "Научно-популярный разбор цифрового тенге: что это, как устроен, чему научили пилоты, сколько стоит и что будет дальше. Данные на 31 октября 2026 года."
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "inLanguage": "ru",
                     "author": {"@type": "Organization", "name": author}, "publisher": {"@type": "Organization", "name": "The Tenge", "url": "https://the-tenge.kz"},
                     "datePublished": ed["cutoff_date"], "dateModified": ed["cutoff_date"], "version": ver}, ensure_ascii=False)
    srcs, ns = sources_li()
    rep = {"TITLE": title, "SHORT": "Третья форма тенге", "DESC": desc, "AUTHOR": author, "VERSION": ver, "DATE": ed["date_text"], "ISO": ed["cutoff_date"],
           "READ": str(read), "COVER": cover_b64(), "BODY": body, "CSS": css, "JS": js, "JSONLD": ld, "SRC": srcs, "NSRC": str(ns),
           "DATA": json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}
    out = tpl
    for k, v in rep.items():
        out = out.replace(f"%%{k}%%", v)
    return out, len(facts), read, words


# ---------------- DOCX / PDF ----------------
def callouts_to_quotes(md):
    out = []; inbox = False
    for line in md.splitlines():
        m = re.match(r"^:::\s*\{\.(short|foryou|note)\}\s*$", line)
        if m: inbox = True; continue
        if inbox and line.strip() == ":::": inbox = False; out.append(""); continue
        out.append(("> " + line if line.strip() else ">") if inbox else line)
    return "\n".join(out)


def static_for(name, F):
    ref = lambda ids: " ".join(f"[{i}]" for i in ids)
    if name == "forms":
        D = load_json("forms.json"); rows = D["rows"]; cs = D["cards"]
        t = "| Свойство | " + " | ".join(c["n"] for c in cs) + " |\n|---|" + "---|" * len(cs) + "\n"
        for k, lab in rows: t += f"| {lab} | " + " | ".join(c[k] for c in cs) + " |\n"
        return t + "\n*Таблица. Три формы тенге* " + ref(["Ф-020", "Ф-084", "Ф-006"]) + "\n"
    if name == "timeline":
        T = load_json("timeline.json"); lab = {"decision": "решение", "pilot": "пилот", "law": "закон", "world": "мир"}
        t = "| Дата | Событие | Что произошло | Тип |\n|---|---|---|---|\n"
        for e in T: t += f"| {e['date'][5:]}.{e['date'][:4]} | {e['title']} | {e['text']} {ref(e['facts'])} | {lab[e['type']]} |\n"
        return t + "\n*Таблица. Хронология проекта, 2020–2026*\n"
    if name == "lifecycle":
        S = load_json("lifecycle.json")
        return "![Путь цифрового тенге: от выпуска до погашения](figures/lifecycle.png){width=100%}\n\n" + "\n".join(f"{i}. **{s['t'][3:]}.** {s['x']} {ref(s['f'])}" for i, s in enumerate(S, 1)) + "\n"
    if name == "marking":
        return ("*Пример (глубина маркировки — 2 звена). Генподрядчик пытается потратить 10 млн условных единиц:*\n\n| Получатель | Результат |\n|---|---|\n"
                "| Свой субподрядчик | разрешено |\n| Поставщик субподрядчика | разрешено |\n| Поставщик поставщика | заблокировано: третий уровень вне глубины |\n"
                "| Посторонняя компания | заблокировано: нет в параметрах маркировки |\n| Вывод из системы | ограничен параметрами маркировки |\n\n"
                "Практически надёжно отследить удаётся 2–3 звена цепочки " + ref(["Ф-009", "Ф-023"]) + "\n")
    if name == "vat":
        return ("*Условный пример при ставке 12% (ставка произвольная): закупка у поставщика на 1 000, продажа покупателю на 1 500.*\n\n"
                "| Шаг | Обычные токены | Токены НДС |\n|---|---|---|\n| Покупатель платит вам | 1 500 | 180 |\n| Вы платите своему поставщику | 1 000 | 120 |\n| Вы отправляете в бюджет | — | 60 |\n\n"
                "Налоговые токены нельзя потратить на другое: они либо идут следующему звену в зачёт, либо в бюджет " + ref(["Ф-010"]) + "\n")
    if name == "issuance": return "![Накопленный выпуск цифровых тенге: заявленные точки](figures/issuance.png){width=100%}\n"
    if name == "scale": return "![Масштаб: выпуск и безналичный оборот](figures/scale.png){width=100%}\n"
    if name == "ladder":
        S = [("Закон № 259-VIII (16.01.2026)", "Определил цифровой тенге; нормы в силе с 18.07.2026", ["Ф-019", "Ф-020"]), ("Правила Нацбанка № 42", "Выпуск, обращение, погашение; в силе с 19.07.2026", ["Ф-054", "Ф-084"]),
             ("Приказ Минфина № 375 (08.06.2026)", "Пилот в бюджетном процессе: платежи свыше 100 млн тенге", ["Ф-085"]), ("Постановление Правительства (23.10.2026)", "Перечень расходов бюджета в цифровом тенге; в силе с 30.10.2026", ["Ф-087"]),
             ("Тарифы НПК (с 06.09.2026)", "135 тенге за документ, минимум 20 000 тенге в месяц", ["Ф-078"])]
        return "| Ступень | Суть |\n|---|---|\n" + "\n".join(f"| {a} | {b} {ref(c)} |" for a, b, c in S) + "\n"
    if name == "faq":
        return "\n\n".join(f"**{q['q']}** {q['a']} {ref(q['facts'])}" for q in load_json("faq.json")) + "\n"
    if name == "tariff":
        return ("![Тариф 135 тенге за документ: доля от суммы платежа](figures/tariff.png){width=100%}\n\n| Сумма платежа | Тариф за документ, % суммы |\n|---|---|\n"
                "| 3 779 тенге (средний чек пилота 2023) | около 3,6% |\n| 100 000 тенге | 0,135% |\n| 100 млн тенге (порог пилота Минфина) | около 0,0001% |\n\n"
                "Минимум 20 000 тенге в месяц соответствует примерно 148 документам " + ref(["Ф-078"]) + "\n")
    if name == "countries":
        C = load_json("countries.json")
        t = "| Страна | Суть | Данные |\n|---|---|---|\n"
        for c in C: t += f"| {c['name']} | {c['summary']} {ref(c['facts'])} | " + "; ".join(f"{a}: {b}" for a, b in c["stats"]) + " |\n"
        return t + "\n*Таблица. Подходы разных стран*\n"
    if name == "risks":
        R = load_json("risks.json")
        return "![Карта рисков](figures/risks.png){width=100%}\n\n" + "\n".join(f"{i}. **{r['name']}.** {r['text']} {ref(r['facts'])}" for i, r in enumerate(R, 1)) + "\n"
    if name == "pace": return "![Темп выпуска: что было и что нужно для целей](figures/pace.png){width=100%}\n"
    if name == "registry": return "Полный реестр фактов этой редакции приведён в приложении «Реестр фактов».\n"
    return ""


def docx_md(chapters, used, ed):
    F = facts_table(); title = "Третья форма тенге"
    head = (f'::: {{custom-style="Title"}}\n{title}\n:::\n\n::: {{custom-style="Subtitle"}}\nкак Казахстан учит деньги выполнять условия\n:::\n\n'
            f"Формат: «Как это работает» · Тема: «Финансы» · Метка: «Научпоп»\n\n**{ed['author_public']}** (the-tenge.kz)\n\n"
            f"**Редакция {ed['public_edition']} · {ed['date_text']}**\n\n"
            "*Материал подготовлен редакцией с использованием инструментов искусственного интеллекта; каждая цифра сверена с источником, сомнительные исключены. Значок вида [Ф-078] отсылает к реестру фактов в приложении.*\n\n")
    parts = []
    for i, (name, t) in enumerate(chapters):
        t = callouts_to_quotes(t) if i == 0 else t
        if i == 0: t = "# Коротко {#short}\n\n" + t
        t = re.sub(r"\[\[(Ф-\d+)\]\]", r"[\1]", t)
        t = re.sub(r"\[([^\]]+)\]\{\.term[^}]*\}", r"\1", t)
        t = re.sub(r"(?m)^\{\{widget:([\w-]+)\}\}\s*$", lambda m: "\n" + static_for(m.group(1), F) + "\n", t)
        parts.append(t)
    G = load_json("glossary.json"); V = load_json("versions.json")
    app = "\n\n# Приложение. Реестр фактов\n\n| Код | Содержание | Источник | Год | Уровень |\n|---|---|---|---|---|\n"
    lv = {"primary": "первичный", "secondary": "пересказ СМИ"}
    for i in sorted(used):
        r = F[i]; app += f"| {i} | {r['content'].replace('|','/')} | {r['source'].replace('|','/')} | {r['year']} | {lv.get(r['level'], r['level'])} |\n"
    app += "\n\n# Словарь терминов\n\n| Термин | Значение и происхождение |\n|---|---|\n" + "".join(f"| {g['term']} | {g['text']} |\n" for g in G)
    app += "\n\n# История версий\n\n" + "\n\n".join(f"**Редакция {v['v']} ({v['date']}).** {v['title']}\n\n" + "\n".join(f"- {c}" for c in v["changes"]) for v in V)
    src = [l.strip() for l in (PUB / "sources.md").read_text(encoding="utf-8").splitlines() if l.strip()]
    app += "\n\n# Список использованных источников\n\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(src, 1)) + "\n"
    return head + "\n\n".join(parts) + app


def build_docs(chapters, used, ed):
    if BUILD.exists(): shutil.rmtree(BUILD)
    (BUILD / "figures").mkdir(parents=True)
    for p in (PUB / "figures").glob("*.png"): shutil.copy(p, BUILD / "figures" / p.name)
    md = "![](figures/cover.png){width=100%}\n\n" + docx_md(chapters, used, ed)
    (BUILD / "full.md").write_text(md, encoding="utf-8")
    env = {"DOC_AUTHOR": ed["author_public"], "DOC_TITLE": "Третья форма тенге: как Казахстан учит деньги выполнять условия",
           "DOC_SUBJECT": "Цифровой тенге, научно-популярный разбор", "TITLE_SPACE_BEFORE": "6"}
    return docxflow.build(BUILD, env)


def joomla_meta(ed, read):
    return {"title": "Третья форма тенге: как Казахстан учит деньги выполнять условия", "alias": "digital-tenge", "format": "how-it-works", "format_ru": "Как это работает",
            "theme": "finance", "theme_ru": "Финансы", "main_tag": "popsci", "main_tag_ru": "Научпоп",
            "tags": [{"name": "Цифровой тенге", "type": "сюжет"}, {"name": "Национальный Банк РК", "type": "регулятор"}, {"name": "НПК", "type": "компания"},
                     {"name": "ЦВЦБ", "type": "сюжет"}, {"name": "Программируемые деньги", "type": "сюжет"}],
            "author": ed["author_public"], "version": ed["public_edition"], "date": ed["cutoff_date"], "reading_minutes": read,
            "lead": "Цифровой тенге — третья форма национальной валюты. Как он устроен, чему научили пилоты, сколько стоит и что будет дальше.",
            "cover": "cover.png", "ai_note": True,
            "ai_note_text": "Материал подготовлен редакцией с использованием инструментов искусственного интеллекта; каждая цифра сверена с источником, сомнительные исключены.",
            "correction_line": "Исправления и история версий — в конце материала.", "files": {"html": f"digital-tenge-popsci-{ed['public_edition']}.html"}}


def main():
    html_only = "--html-only" in sys.argv
    ed = edition(); chapters = read_chapters()
    blobs = [load_json(n) for n in ("timeline.json", "faq.json", "countries.json", "risks.json", "lifecycle.json", "forms.json")]
    used, errs, warns = gate(chapters, blobs)
    typo = typo_check(chapters)
    for w in warns: print("ПРЕДУПРЕЖДЕНИЕ:", w)
    for e in errs + typo: print("ОШИБКА:", e)
    if errs or typo: sys.exit("Сборка остановлена: в публичном тексте недопустимые ссылки или типографика.")
    vs = load_json("versions.json")
    if vs[0]["v"] != ed["public_edition"]:
        sys.exit(f"versions.json: последняя версия {vs[0]['v']} не совпадает с public_edition {ed['public_edition']}")
    DIST.mkdir(exist_ok=True)
    html, nf, read, words = build_html(chapters, used, ed)
    ver = ed["public_edition"]
    (DIST / f"digital-tenge-popsci-{ver}.html").write_text(html, encoding="utf-8")
    shutil.copy(PUB / "figures" / "cover.png", DIST / f"digital-tenge-popsci-{ver}-cover.png")
    json.dump(joomla_meta(ed, read), open(DIST / f"digital-tenge-popsci-{ver}-meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if html_only:
        print(f"Готово (только HTML): {len(html)//1024} КБ; фактов {nf}; чтение ≈{read} мин."); return
    docx, pdf, pages = build_docs(chapters, used, ed)
    shutil.copy(docx, DIST / f"digital-tenge-popsci-{ver}.docx"); shutil.copy(pdf, DIST / f"digital-tenge-popsci-{ver}.pdf")
    print(f"Готово: HTML {len(html)//1024} КБ; фактов в редакции {nf}; слов ≈{words}; чтение ≈{read} мин.; docx/PDF {pages} стр.")


if __name__ == "__main__":
    main()
