"""Проверка интерактивности публичной HTML-редакции в headless Chromium (Playwright). Запуск: python scripts/test_public_html.py [файл.html]"""
import sys, json
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
f = Path(sys.argv[1]) if len(sys.argv) > 1 else next((root / "dist").glob("digital-tenge-popsci-*.html"))
shots = Path("/tmp/shots"); shots.mkdir(exist_ok=True)
errors, ok = [], []

def check(cond, name):
    (ok if cond else errors).append(name)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    msgs = []
    pg.on("console", lambda m: msgs.append((m.type, m.text)) if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: msgs.append(("pageerror", str(e))))
    pg.goto(f.resolve().as_uri()); pg.wait_for_timeout(400)
    # 1. каркас
    check(pg.locator("main section.level1").count() >= 11, "разделы-главы построены")
    check(pg.locator("nav.toc a").count() >= 11, "оглавление построено")
    check(pg.locator("[data-widget]").count() >= 16, "виджеты на месте")
    check(pg.locator("span.fact").count() > 60, "значки фактов есть")
    check(pg.evaluate("document.querySelectorAll('.widget').length") == pg.evaluate("Array.from(document.querySelectorAll('.widget')).filter(w=>w.children.length>0).length"), "ни один виджет не пуст")
    # 2. всплывающая карточка факта
    pg.locator("span.fact").first.click(); pg.wait_for_timeout(100)
    check(pg.locator("#pop").is_visible() and "Источник" in pg.locator("#pop").inner_text(), "карточка факта открывается")
    pg.keyboard.press("Escape"); check(not pg.locator("#pop").is_visible(), "карточка закрывается по Esc")
    # 3. подсказка термина
    pg.locator("span.term").first.scroll_into_view_if_needed(); pg.locator("span.term").first.hover(); pg.wait_for_timeout(100)
    check(pg.locator("#tip").is_visible(), "подсказка термина появляется")
    # 4. формы
    w = pg.locator('[data-widget="forms"]'); w.scroll_into_view_if_needed(); w.locator("button.chip").nth(3).click()
    check("on" in (w.locator(".kv").nth(3).get_attribute("class") or ""), "формы: подсветка строки")
    # 5. хронология
    w = pg.locator('[data-widget="timeline"]'); w.scroll_into_view_if_needed(); n0 = w.locator(".ev").count()
    w.locator("button.chip").nth(3).click(); n1 = w.locator(".ev").count()
    check(0 < n1 < n0, f"хронология: фильтр ({n0}->{n1})")
    w.locator(".ev button").first.click(); check(w.locator(".ev.open").count() == 1, "хронология: раскрытие")
    # 6. жизненный цикл
    w = pg.locator('[data-widget="lifecycle"]'); w.scroll_into_view_if_needed()
    t0 = w.locator(".out").inner_text(); w.get_by_role("button", name="дальше →").click(); t1 = w.locator(".out").inner_text()
    check(t0 != t1 and "Цифровой счёт" in t1, "жизненный цикл: шаги")
    # 7. маркировка
    w = pg.locator('[data-widget="marking"]'); w.scroll_into_view_if_needed(); w.get_by_role("button", name="Посторонней компании").click()
    check("Заблокировано" in w.locator(".out").inner_text(), "маркировка: блокировка постороннего")
    w.get_by_role("button", name="3 звена").click(); w.get_by_role("button", name="Поставщику поставщика").click()
    check("Разрешено" in w.locator(".out").inner_text(), "маркировка: глубина 3 разрешает третий уровень")
    # 8. НДС
    w = pg.locator('[data-widget="vat"]'); w.scroll_into_view_if_needed()
    check("60" in w.locator("table").inner_text(), "НДС: по умолчанию в бюджет 60")
    w.locator('input[type=number]').nth(1).fill("2000"); w.locator('input[type=number]').nth(1).dispatch_event("input")
    check("120" in w.locator("table").inner_text().replace("\u00a0", ""), "НДС: пересчёт (2000-1000)*12%=120")
    # 9. выпуск и масштаб
    w = pg.locator('[data-widget="issuance"]'); w.scroll_into_view_if_needed(); w.locator("circle").nth(1).click()
    check("336,6" in w.locator(".out").inner_text(), "график выпуска: точка")
    w.get_by_role("button", name="Приблизить").click(); check(w.locator("circle").count() == 4, "график выпуска: переключение оси")
    w = pg.locator('[data-widget="scale"]'); w.scroll_into_view_if_needed(); w.get_by_role("button", name="Логарифмическая").click()
    check("0,2%" in w.locator(".out").inner_text(), "масштаб: подпись про 0,2%")
    # 10. лестница и FAQ
    w = pg.locator('[data-widget="ladder"] details'); check(w.count() == 5, "лестница норм: 5 ступеней")
    q = pg.locator('[data-widget="faq"] details'); check(q.count() == 9, "FAQ: 9 вопросов")
    q.first.locator("summary").click(); check(q.first.get_attribute("open") is not None, "FAQ: раскрытие")
    # 11. тариф
    w = pg.locator('[data-widget="tariff"]'); w.scroll_into_view_if_needed()
    r = w.locator('input[type=range]'); r.evaluate("e=>{e.value=8;e.dispatchEvent(new Event('input'))}")
    txt = w.locator(".out").inner_text().replace("\u00a0", " ")
    check("0,00013" in txt.replace(" ", "") or "0,00014" in txt.replace(" ", "") or "0,0001" in txt.replace(" ", ""), "тариф: доля для 100 млн")
    w.locator('input[type=number]').fill("10"); w.locator('input[type=number]').dispatch_event("input")
    check("20" in w.locator(".out").inner_text().replace("\u00a0", ""), "тариф: действует минимум 20 000")
    # 12. страны, риски, темп
    w = pg.locator('[data-widget="countries"]'); w.scroll_into_view_if_needed(); a = w.locator(".card").count(); w.get_by_role("button", name="принуждение").first.click()
    check(0 < w.locator(".card").count() < a, "страны: фильтр")
    w = pg.locator('[data-widget="risks"]'); w.scroll_into_view_if_needed(); w.locator("svg g").nth(0).click()
    check("Плохие данные" in w.locator(".out").inner_text(), "риски: карточка риска")
    w = pg.locator('[data-widget="pace"]'); w.scroll_into_view_if_needed()
    check("138" in w.locator(".out").inner_text().replace("\u00a0", ""), "темп: для 2 трлн за 12 мес. ≈138")
    # 13. реестр, словарь, версии
    w = pg.locator('[data-widget="registry"]'); w.scroll_into_view_if_needed(); total = w.locator("tbody tr").count()
    w.locator("input.search").fill("тариф"); w.locator("input.search").dispatch_event("input"); fil = w.locator("tbody tr").count()
    check(0 < fil < total, f"реестр: поиск ({total}->{fil})")
    w = pg.locator('[data-widget="glossary"]'); w.scroll_into_view_if_needed(); w.locator("input.search").fill("оракул"); w.locator("input.search").dispatch_event("input")
    check(w.locator("details").count() == 1, "словарь: поиск")
    w = pg.locator('[data-widget="versions"]'); w.scroll_into_view_if_needed(); w.locator("select").select_option("1.0")
    check("Первая аналитическая" in w.locator(".out").inner_text(), "версии: выбор версии")
    # 14. тема, шрифт, прогресс
    pg.locator("#theme").click(); check(pg.evaluate("document.documentElement.getAttribute('data-theme')") in ("dark", "light"), "переключатель темы")
    pg.locator("#fsp").click(); check(pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--tm-fs').trim()") == "20px", "размер шрифта")
    # 15. снимки
    pg.evaluate("window.scrollTo(0,0)"); pg.screenshot(path=str(shots / "top.png"))
    for name in ("lifecycle", "marking", "tariff", "risks", "pace", "issuance", "timeline", "countries"):
        el = pg.locator(f'[data-widget="{name}"]'); el.scroll_into_view_if_needed(); el.screenshot(path=str(shots / f"w-{name}.png"))
    pg.locator("#theme").click()
    m = b.new_page(viewport={"width": 390, "height": 800}, device_scale_factor=2); m.goto(f.resolve().as_uri()); m.wait_for_timeout(300)
    m.screenshot(path=str(shots / "mobile-top.png"))
    ov = m.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
    check(not ov, "мобильная вёрстка без горизонтальной прокрутки")
    for typ, text in msgs: errors.append(f"консоль {typ}: {text}")
    b.close()

print(f"Пройдено проверок: {len(ok)}")
for e in errors: print("ПРОВАЛ:", e)
sys.exit(1 if errors else 0)
