"""Типографический проход «Мильчин» (beaverbeard/milchin) с защитой разметки доклада.

Мильчин — детерминированный типограф: неразрывные пробелы, тире, кавычки, юникод-гигиена.
Перед ним прячем то, что для Pandoc и сборки — синтаксис, а не текст:
  ::: {custom-style="…"}, {#якорь}, {{плейсхолдеры}} и {{widget:…}}, <!-- комментарии -->,
  [[Ф-NNN]], \\newpage, номера норм через дефис (глава 7-1, ст. 4-2, пп. 62-4)),
  а также весь список источников по ГОСТ (там «–» — знак области описания, а не тире).
Инициалы остаются слитными («Т.Сулейменов»): так принято в докладе.

Запуск: python scripts/typograph.py [--check] файл...
Путь к milchin.py — переменная MILCHIN, по умолчанию
tools/redkollegiya/milchin/.claude/skills/milchin/milchin.py (ставит scripts/redkollegiya_setup.sh).
"""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MILCHIN = os.environ.get("MILCHIN", str(ROOT / "tools/redkollegiya/milchin/.claude/skills/milchin/milchin.py"))
PROTECT = [
    (r"^:::.*$", re.M),                  # блоки custom-style
    (r"\{#[^}\n]+\}", 0),                # якоря заголовков
    (r"\{\{[^}\n]+\}\}", 0),             # плейсхолдеры и виджеты
    (r"<!--.*?-->", re.S),               # служебные комментарии
    (r"\[\[[^\]\n]+\]\]", 0),            # значки фактов публичной редакции
    (r"\\newpage", 0),
    (r"\{[.#][^}\n]*\}", 0),        # атрибуты Pandoc: [термин]{.term data-t="…"}
    (r"(?<![\d.])\d+-\d+\)?", 0),        # номера норм: 7-1, 4-2, 62-4)
]
STOP = "# Список использованных источников"
MARK = re.compile(r"QZPROT(\d{4})QZ")


def run(text, check=False):
    head, sep, tail = text.partition(STOP)
    store = []

    def keep(m):
        store.append(m.group(0))
        return f"QZPROT{len(store) - 1:04d}QZ"

    # английские кавычки “…” внутри русского текста — это вложенные кавычки: «… „…“ …»
    masked = re.sub(r"“([^”\n]*)”", r"„\1“", head)
    for pat, flags in PROTECT:
        masked = re.sub(pat, keep, masked, flags=flags)
    args = [sys.executable, MILCHIN, "--no-initials-space", "--check" if check else "--fix"]
    p = subprocess.run(args, input=masked, capture_output=True, text=True, check=True)
    if check:
        return text, p.stderr
    out = MARK.sub(lambda m: store[int(m.group(1))], p.stdout)
    if "QZPROT" in out or len(MARK.findall(p.stdout)) != len(store):
        raise SystemExit("Мильчин повредил защищённые зоны: число маркеров не совпало")
    if head.endswith("\n") and not out.endswith("\n"):
        out += "\n"
    return out + sep + tail, p.stderr


if __name__ == "__main__":
    check = "--check" in sys.argv
    for f in [a for a in sys.argv[1:] if not a.startswith("--")]:
        path = Path(f)
        src = path.read_text(encoding="utf-8")
        out, log = run(src, check)
        if not check and out != src:
            path.write_text(out, encoding="utf-8")
        last = log.strip().splitlines()[-1] if log.strip() else "без правок"
        print(f"{f}: {last}")
