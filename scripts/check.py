"""Проверка целостности доклада: коды Ф-/Р-/М-/R-, ссылки, счётчики.
Запуск: python scripts/check.py  (код возврата 1 при ошибках)."""
import re, sys
from common import assemble, read_csv


def run(verbose=True):
    text, subs = assemble()
    body = text[: text.index("# Приложение А")]
    errors, warns = [], []
    facts = read_csv("facts.csv")
    ids = [int(r["id"].split("-")[1]) for r in facts]
    if ids != list(range(1, len(ids) + 1)):
        errors.append("Нумерация Ф- не непрерывна или есть дубли")
    reg = set(ids)
    ref = {int(x) for x in re.findall(r"Ф-(\d+)", body)}
    miss = sorted(ref - reg)
    if miss:
        errors.append(f"Ссылки на отсутствующие факты: {miss}")
    unused = sorted(reg - ref)
    if unused:
        warns.append(f"Факты реестра, на которые нет ссылок в тексте: {unused}")
    for code, csvname in (("Р", "discrepancies.csv"), ("М", "gaps.csv")):
        defined = {r["id"] for r in read_csv(csvname)}
        used = set(re.findall(rf"{code}-\d+", body))
        if used - defined:
            errors.append(f"Ссылки на неопределённые {code}-коды: {sorted(used - defined)}")
        if defined - used:
            warns.append(f"{code}-коды без ссылок в тексте: {sorted(defined - used)}")
    rdef = set(re.findall(r"\| (R-\d+) \|", text))
    rused = set(re.findall(r"R-\d+", body))
    if rused - rdef:
        errors.append(f"Ссылки на неопределённые R-коды: {sorted(rused - rdef)}")
    if "{{" in text:
        errors.append("Остались нераскрытые плейсхолдеры {{...}}")
    for r in facts:
        if r.get("status") == "superseded" and r.get("superseded_by") not in {x["id"] for x in facts}:
            errors.append(f"{r['id']}: заменённый факт без существующего superseded_by")
        if not r["source"].strip() or not r["year"].strip():
            errors.append(f"{r['id']}: пустой источник или год данных")
    if verbose:
        print(f"Фактов: {len(facts)}; расхождений: {subs['N_DISC']}; белых пятен: {subs['N_GAPS']}; проверка ИИ: {subs['N_AI']}")
        for w in warns: print("ПРЕДУПРЕЖДЕНИЕ:", w)
        for e in errors: print("ОШИБКА:", e)
        print("Целостность:", "НЕ ПРОЙДЕНА" if errors else "пройдена")
    return errors, warns


if __name__ == "__main__":
    e, _ = run()
    sys.exit(1 if e else 0)
