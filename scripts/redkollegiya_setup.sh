#!/usr/bin/env bash
# Ставит русскую Редколлегию (beaverbeard/redkollegiya, MIT) и пятёрку её редакторов в tools/redkollegiya/
# на закреплённых коммитах. Папка в .gitignore: чужой код в репозиторий доклада не кладём.
# Казахская Редколлегия (bsakhanov/kk-redkollegiya) — для будущей казахской версии публичной редакции.
# Обновить закрепление: поменять хэш ниже, прогнать языковой проход на одном томе, сравнить diff.
set -e
cd "$(dirname "$0")/.."
D=tools/redkollegiya; mkdir -p "$D"
pin() { # имя репозиторий коммит
  if [ ! -d "$D/$1/.git" ]; then git clone -q "https://github.com/$2.git" "$D/$1"; fi
  git -C "$D/$1" fetch -q origin && git -C "$D/$1" checkout -q "$3" && echo "$1 → $3"
}
pin redkollegiya beaverbeard/redkollegiya a45052294bbc49cdcdacd0c916dd5bd5352b695e
pin chukovsky    beaverbeard/chukovsky    16062b53152456811b28316963ca6ea1e0c921ec
pin agranovsky   beaverbeard/agranovsky   67349d5fa94a42ce99e086ff7005031024c5ec26
pin slopotron    beaverbeard/slopotron    907dcc52222d84cd1f65a3dfb79c06b4ecf9f187
pin rozental     beaverbeard/rozental     1972f915edf4271dab16e6e4cafb2203886e741d
pin milchin      beaverbeard/milchin      37ee403e98a3b1b6537ef3f9b9218d18e863d28c
pin kk-redkollegiya bsakhanov/kk-redkollegiya 3bb5f784306ae3ac21b90f11ceb2de01cd378d81
python3 "$D/milchin/.claude/skills/milchin/milchin.py" --selftest | tail -1
python3 "$D/redkollegiya/.claude/skills/redkollegiya/apply.py" --selftest | tail -1
