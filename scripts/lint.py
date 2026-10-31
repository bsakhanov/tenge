"""Типографика и язык по правилам автора (см. methodology/typography-and-language.md).
Запуск: python scripts/lint.py [файл...]. Это предупреждения для ручного разбора, не запреты."""
import re, sys
from common import SRC, ORDER, ROOT

ABBR_OK = set("НБРК НПК ЦВЦБ БВУ ЦТ НДС ЭСФ ПОД ФТ ВВП МВФ БМР КГД ОПЭ НЦФИ ТСП ДБО ИСЖ ГИСС МСПК КНР ОАЭ США ЕЦБ НБК ГБД СПК ФРП ИС КАЗ DSGE UTXO CBDC DLT DvP PvP HSM NFC QR POS API ISO KASE SWIFT UPI TPS ERP MVP SIM PBM CNY HKD VAT SQL BES EUR CHF AUD MYR SGD SAR THB AED ILS NOK SEK III VIII NNN QADAM EDITION DATE СМИ CDB ИЗПИ RBK BNK КТЖ МСМП ПРАЙМ CIPS IDC IMF CAFS ЖКХ РФ ЕС BIS".split())
ABBR_PREV = {"ст", "п", "пп", "с", "г", "гг", "№", "рис", "табл", "см", "тыс", "т", "др", "ч"}
CHECKS = [
    ("прямые кавычки (нужны «ёлочки»)", r'(?<!=)(?<![\w-]=)"(?![^"\n]*\})'),
    ("дефис вместо длинного тире", r" - "),
    ("«является/являются» (лучше глагол по смыслу)", r"\bявля(ется|ются|лся|лась|лось|лись)\b"),
    ("«данный» как указательное слово (лучше «этот»)", r"\bданн(ый|ая|ое|ому|ого|ой|ую)\b"),
    ("пробел перед %", r"\d %"),
    ("«млн.» «млрд.» с точкой", r"\b(млн|млрд|трлн)\.(?=\s[а-я])"),
    ("десятичная точка вместо запятой", r"(?<![\d.\-А-Яа-яA-Za-z№])\d{1,3}\.\d{1,2}(?![\d.])(?!\s*(?:Часть|\.))"),
]
# Кальки и обороты из каталога языкового прогона (methodology/language-pass.md, раздел 4).
# Это подсказки для редактора: вне цитат такие места почти всегда стоит переписать.
CALQUES = [
    r"на рельсах", r"ранн\w+ пользовател", r"краткосрочной перспектив", r"до не менее",
    r"розничн\w+ принят", r"\bдизайн\w*", r"в формат\w? цифров", r"\bэффект на ",
    r"на всех (банков|компаний|организаций)", r"\(\w+ против \w+\)", r"функционал\w*",
    r"\bвалидн\w+|\bвалидир\w+", r"вендорск\w+", r"продуктивн\w+ (ЦВЦБ|решени\w+|сред\w+)",
    r"\bсесси[яиюей]\b", r"мажорн\w+|минорн\w+", r"модел\w+ дохода", r"за около",
    r"в рамках", r"на сегодняшний день", r"играет? (ключевую|важную) роль", r"\bосуществля\w+",
    r"позволяет (сделать|осуществ)", r"источник\w* правды", r"в реальном времени",
    r"важно (отметить|подчеркнуть)|стоит (отметить|подчеркнуть)", r"давайте разбер",
]
CHECKS += [(f"калька или штамп ({c})", c) for c in CALQUES]


SECTION_CTX = re.compile(r"(част[ьи]|[Тт]абл\w*|[Рр]ис\w*|см\.|п\.|разделы?|тома?|Том)\s*[\d.,и\s–-]*$")


def lint_text(name, text):
    text = re.sub(r"<!--.*?-->", lambda m: " " * len(m.group(0)), text, flags=re.S)
    out = []
    for title, pat in CHECKS:
        for m in re.finditer(pat, text):
            if title.startswith("десятичная") and SECTION_CTX.search(text[max(0, m.start() - 24): m.end()]):
                continue
            line = text.count("\n", 0, m.start()) + 1
            ctx = text[max(0, m.start() - 30): m.end() + 30].replace("\n", " ")
            out.append(f"{name}:{line}: {title}: …{ctx}…")
    for m in re.finditer(r"\b[А-ЯЁA-Z]{3,}\b", text):
        if m.group(0) not in ABBR_OK:
            line = text.count("\n", 0, m.start()) + 1
            out.append(f"{name}:{line}: слово прописными (не из белого списка аббревиатур): {m.group(0)}")
    for m in re.finditer(r"(\S+)\. (\d)", text):
        if text[text.rfind("\n", 0, m.start()) + 1:].startswith("#"):
            continue
        if m.group(1).lower().strip("(«)") not in ABBR_PREV:
            line = text.count("\n", 0, m.start()) + 1
            out.append(f"{name}:{line}: предложение начинается с цифры: …{text[m.start():m.end()+25]}…")
    return out


if __name__ == "__main__":
    files = [ROOT / a for a in sys.argv[1:]] or [SRC / f"{n}.md" for n in ORDER]
    res = []
    for f in files:
        t = f.read_text(encoding="utf-8")
        if f.name == "appendix.md":
            t = t[: t.find("# Список использованных источников")]
        res += lint_text(f.name, t)
    print("\n".join(res) if res else "Замечаний нет")
    print(f"Всего замечаний: {len(res)}")
