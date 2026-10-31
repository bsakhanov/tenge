"""Страж языкового прохода: сравнивает файл с версией в git (по умолчанию HEAD) и проверяет,
что правка языка не задела фактуру и разметку.

Проверяется: мультимножество кодов (Ф-, Р-, М-, R-, [[Ф-…]]), чисел, плейсхолдеров {{…}},
ссылок и адресов, число заголовков и строк таблиц; прямые цитаты в «ёлочках» длиной от 6 слов
(цитаты источников не переписываются); коридор объёма (−10% … +10% знаков).
Для JSON дополнительно: файл разбирается, ключи и структура не меняются.

Запуск: python scripts/langpass_guard.py файл... [--ref HEAD]
Код возврата 1, если есть нарушения. Это страж, а не судья: число, сознательно записанное словом
(«десять» вместо «10»), допустимо, но такие случаи надо назвать в отчёте прохода.
"""
import json, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAT = {
    "коды": r"\[\[Ф-\d+\]\]|[ФРМ]-\d+|R-\d+",
    "числа": r"\d+(?:[ ,. ]\d+)*",
    "плейсхолдеры": r"\{\{[^}]+\}\}|<!--.*?-->|\{[.#][^}\n]*\}",
    "адреса": r"https?://\S+",
}


def old_version(path, ref):
    rel = Path(path).resolve().relative_to(ROOT)
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{rel.as_posix()}"],
                          capture_output=True, text=True, check=True).stdout


def norm(s):
    return s.replace(" ", " ")


def quotes(t):
    out = []
    for q in re.findall(r"«([^«»]{30,}?)»", t):
        if len(q.split()) >= 6:
            out.append(re.sub(r"\s+", " ", q.strip()))
    return Counter(out)


def json_shape(o):
    if isinstance(o, dict):
        return {k: json_shape(v) for k, v in o.items()}
    if isinstance(o, list):
        return [json_shape(v) for v in o]
    return type(o).__name__


def check(path, ref):
    new, old = norm(Path(path).read_text(encoding="utf-8")), norm(old_version(path, ref))
    errs = []
    for name, pat in PAT.items():
        a, b = Counter(re.findall(pat, old, re.S)), Counter(re.findall(pat, new, re.S))
        if a != b:
            lost, added = a - b, b - a
            errs.append(f"{name}: пропало {dict(lost)} ; появилось {dict(added)}")
    for name, pat in (("заголовки", r"^#+ "), ("строки таблиц", r"^\|")):
        a, b = len(re.findall(pat, old, re.M)), len(re.findall(pat, new, re.M))
        if a != b:
            errs.append(f"{name}: было {a}, стало {b}")
    qa, qb = quotes(old), quotes(new)
    lost = qa - qb
    if lost:
        errs.append("изменены или удалены прямые цитаты: " + " | ".join(list(lost)[:5]))
    ratio = len(new) / max(1, len(old))
    if not 0.9 <= ratio <= 1.1:
        errs.append(f"объём изменился на {100 * (ratio - 1):+.1f}% (коридор ±10%)")
    if path.endswith(".json"):
        try:
            if json_shape(json.loads(new)) != json_shape(json.loads(old)):
                errs.append("JSON: изменилась структура")
        except json.JSONDecodeError as e:
            errs.append(f"JSON не разбирается: {e}")
    return errs, ratio


if __name__ == "__main__":
    args = sys.argv[1:]
    ref = "HEAD"
    if "--ref" in args:
        i = args.index("--ref"); ref = args[i + 1]; del args[i:i + 2]
    bad = 0
    for f in args:
        errs, ratio = check(f, ref)
        print(f"{f}: объём {100 * (ratio - 1):+.1f}% — " + ("чисто" if not errs else "ЗАМЕЧАНИЯ"))
        for e in errs:
            print("   ", e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)
