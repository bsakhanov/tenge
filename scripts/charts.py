"""Статические иллюстрации для docx/PDF публичной редакции (matplotlib). Интерактивные версии рисует JS в HTML."""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from common import edition
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import matplotlib.dates as mdates
from datetime import date

OUT = Path(__file__).resolve().parent.parent / "report" / "public" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
G, G2, AMB, GR, INK, BG = "#0b6e4f", "#b4572a", "#b7791f", "#6b7280", "#1d1d1f", "#fbfaf7"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#9a9a9a", "axes.labelcolor": INK, "text.color": INK, "figure.facecolor": "white"})


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


def issuance():
    pts = [(date(2025, 7, 11), 257.5, "257,5 (июль 2025)"), (date(2025, 12, 31), 336.6, "336,6 (конец 2025)"), (date(2026, 6, 15), 340.0, "≈340 (июнь 2026)")]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=G, lw=2.2, marker="o", ms=8)
    for x, y, t in pts:
        ax.annotate(t, (x, y), textcoords="offset points", xytext=(18 if x==xs[0] else 0, 12), ha="center", fontsize=10)
    ax.set_ylim(200, 380); ax.set_ylabel("млрд тенге"); ax.set_xlim(date(2025, 5, 15), date(2026, 8, 15))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m.%Y"))
    ax.grid(axis="y", color="#e5e5e5")
    ax.set_title("Накопленный выпуск цифровых тенге: три заявленные точки", fontsize=12, loc="left")
    ax.text(0.01, -0.22, "Источники: Ф-096, Ф-102, Ф-088. Между точками линия условная; на 1 июля 2025 года и позже данных нет.", transform=ax.transAxes, fontsize=8.5, color=GR)
    save(fig, "issuance")


def scale():
    fig, ax = plt.subplots(figsize=(8, 2.8))
    vals = [336.6, 166100.0]; labs = ["Накопленный выпуск цифровых тенге\n(конец 2025 года)", "Безналичные платежи\n(оборот за 2024 год)"]
    ax.barh(labs, vals, color=[G, GR], height=0.5); ax.set_xscale("log"); ax.set_xlim(100, 600000)
    ax.set_xlabel("млрд тенге, логарифмическая шкала")
    ax.text(336.6 * 1.25, 0, "336,6 млрд", va="center", fontsize=10); ax.text(166100 * 0.28, 1, "166,1 трлн", va="center", ha="right", color="white", fontsize=10)
    ax.set_title("Масштаб: около 0,2% годового безналичного оборота (расчёт редакции)", fontsize=12, loc="left")
    ax.text(0, -0.5, "Источники: Ф-102, Ф-003. Сравниваются накопленный выпуск и годовой оборот, это порядок величин, а не точная доля.", transform=ax.transAxes, fontsize=8.5, color=GR)
    save(fig, "scale")


def tariff():
    fig, ax = plt.subplots(figsize=(8, 3.8))
    xs = [10 ** (3 + i * 0.05) for i in range(0, 121)]  # 1 тыс .. 1 млрд
    ys = [135 / x * 100 for x in xs]
    ax.plot(xs, ys, color=G, lw=2.2); ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("сумма платежа, тенге"); ax.set_ylabel("тариф за документ, % суммы")
    for x, t, dy in [(3779, "средний чек розничного\nпилота 2023: 3,6%", 18), (1e8, "порог пилота Минфина,\n100 млн: 0,0001%", 18)]:
        y = 135 / x * 100
        ax.plot([x], [y], "o", color=G2, ms=8); ax.annotate(t, (x, y), textcoords="offset points", xytext=(10, dy), fontsize=9.5)
    ax.grid(color="#e5e5e5", which="major")
    ax.set_title("Тариф 135 тенге за документ: доля от суммы платежа", fontsize=12, loc="left")
    ax.text(0.01, -0.25, "Источники: Ф-078, Ф-035, Ф-085. Тариф платят участники платформы; переложат ли его на клиентов, неизвестно.", transform=ax.transAxes, fontsize=8.5, color=GR)
    save(fig, "tariff")


def risks():
    import json
    R = json.load(open(OUT.parent / "data" / "risks.json", encoding="utf-8"))
    fig = plt.figure(figsize=(9.6, 5.0)); ax = fig.add_axes([0.07, 0.14, 0.50, 0.74])
    ax.set_xlim(0.5, 3.5); ax.set_ylim(0.5, 3.5); ax.set_xticks([1, 2, 3]); ax.set_yticks([1, 2, 3])
    ax.set_xticklabels(["низкая", "средняя", "высокая"]); ax.set_yticklabels(["умеренные", "заметные", "тяжёлые"])
    ax.set_xlabel("вероятность (оценка редакции)"); ax.set_ylabel("последствия (оценка редакции)")
    for x0 in (0.5, 1.5, 2.5):
        for y0 in (0.5, 1.5, 2.5):
            heat = (x0 + y0 - 1) / 5
            ax.add_patch(plt.Rectangle((x0, y0), 1, 1, color=(0.72, 0.35, 0.16, 0.05 + 0.13 * heat), zorder=0))
    ax.grid(color="#e5e5e5")
    slots = {}
    for n, r in enumerate(R, 1):
        key = (r["p"], r["i"]); k = slots.get(key, 0); slots[key] = k + 1
        dx = (k % 2) * 0.30 - 0.15; dy = (k // 2) * -0.30 + 0.12
        ax.plot([r["p"] + dx], [r["i"] + dy], "o", color=G2, ms=17, zorder=3)
        ax.text(r["p"] + dx, r["i"] + dy, str(n), color="white", ha="center", va="center", fontsize=10, weight="bold", zorder=4)
    ax.set_title("Карта рисков", fontsize=12, loc="left")
    fig.text(0.62, 0.84, "Расшифровка", fontsize=11, weight="bold")
    for n, r in enumerate(R, 1):
        fig.text(0.62, 0.78 - (n - 1) * 0.095, f"{n}. {r['name']}", fontsize=10.5)
    save(fig, "risks")


def pace():
    fig, ax = plt.subplots(figsize=(8, 3.6))
    labs = ["2 пол. 2025\n(факт по точкам)", "1 пол. 2026\n(факт по точкам)", "нужно для 1 трлн\nза 12 месяцев", "нужно для 2 трлн\nза 12 месяцев"]
    vals = [13.95, 0.6, (1000 - 340) / 12, (2000 - 340) / 12]
    ax.bar(labs, vals, color=[G, G, AMB, G2], width=0.55)
    for i, v in enumerate(vals):
        ax.text(i, v + 3, f"≈{v:.0f}".replace(".", ",") if v >= 1 else "<1", ha="center", fontsize=10)
    ax.set_ylabel("млрд тенге в месяц"); ax.set_ylim(0, 160)
    ax.set_title("Темп выпуска: что было и что нужно для заявленных целей", fontsize=12, loc="left")
    ax.text(0, -0.3, "Расчёт редакции по Ф-096, Ф-102, Ф-088; предполагается, что цель означает накопленный выпуск от уровня около 340 млрд.", transform=ax.transAxes, fontsize=8.5, color=GR)
    save(fig, "pace")


def lifecycle():
    fig, ax = plt.subplots(figsize=(9.6, 3.3)); ax.axis("off"); ax.set_xlim(0, 10.6); ax.set_ylim(0, 3.2)
    boxes = [(0.1, "Нацбанк", "выпускает и\nпогашает"), (2.2, "Банк", "счёт клиента,\nличность"), (4.3, "Клиент", "кошелёк в\nприложении"), (6.4, "Продавец", "принимает\nплатёж"), (8.6, "Банк\nпродавца", "возврат в\nбезналичные")]
    for x, t, s in boxes:
        ax.add_patch(FancyBboxPatch((x, 1.2), 1.6, 1.3, boxstyle="round,pad=0.04", fc="#e8f3ee", ec=G, lw=1.6))
        ax.text(x + 0.8, 2.15, t, ha="center", va="center", fontsize=9.5, weight="bold"); ax.text(x + 0.8, 1.6, s, ha="center", va="center", fontsize=8.5)
    for i in range(len(boxes) - 1):
        ax.add_patch(FancyArrowPatch((boxes[i][0] + 1.67, 1.85), (boxes[i + 1][0] - 0.05, 1.85), arrowstyle="-|>", mutation_scale=14, color=G))
    ax.text(5, 0.55, "Нотариальная нода проверяет, что токен не потрачен дважды; оракул сообщает условия из внешних систем", ha="center", fontsize=9, color=INK)
    ax.set_title("Путь цифрового тенге: от выпуска до погашения", fontsize=12, loc="left")
    save(fig, "lifecycle")


def cover():
    fig = plt.figure(figsize=(16, 9), dpi=100); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
    import numpy as np
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(grad, extent=[0, 16, 0, 9], cmap=matplotlib.colors.LinearSegmentedColormap.from_list("g", ["#07382a", "#0b6e4f", "#16805f"]), aspect="auto", zorder=0)
    import random
    random.seed(7); nodes = [(random.uniform(8.5, 15.6), random.uniform(0.6, 8.4)) for _ in range(26)]
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            d = math.hypot(a[0] - b[0], a[1] - b[1])
            if d < 2.6: ax.plot([a[0], b[0]], [a[1], b[1]], color="white", alpha=0.18, lw=1)
    for x, y in nodes: ax.add_patch(Circle((x, y), 0.09, color="white", alpha=0.7))
    ax.add_patch(Circle((12.4, 4.5), 1.9, fc="none", ec="#ffd9a0", lw=5, alpha=0.9)); ax.add_patch(Circle((12.4, 4.5), 1.55, fc="none", ec="white", lw=2, alpha=0.6))
    ax.text(12.4, 4.5, "₸", ha="center", va="center", fontsize=120, color="#ffd9a0", weight="bold", family="DejaVu Sans")
    ax.text(0.8, 6.9, "Научпоп · Как это работает", fontsize=20, color="#ffd9a0", va="center")
    ax.text(0.8, 5.2, "Третья форма тенге", fontsize=54, color="white", weight="bold", va="center")
    ax.text(0.8, 3.9, "как Казахстан учит деньги\nвыполнять условия", fontsize=30, color="white", va="center", linespacing=1.3)
    ax.text(0.8, 1.2, f"The Tenge · редакция {edition()['public_edition']} · данные на {edition()['date_text']}", fontsize=18, color="#cfe9df", va="center")
    fig.savefig(OUT / "cover.png", dpi=100); fig.savefig(OUT / "cover.svg"); plt.close(fig)


if __name__ == "__main__":
    for f in (issuance, scale, tariff, risks, pace, lifecycle, cover):
        f()
    print("figures:", sorted(p.name for p in OUT.glob("*")))
