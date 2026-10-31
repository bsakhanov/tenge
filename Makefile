.PHONY: check lint build public html charts test-public manifest snapshot all
check:
	python3 scripts/check.py
lint:
	python3 scripts/lint.py
build:            # аналитическая редакция (шесть томов): docx и PDF
	python3 scripts/make.py
charts:           # статические иллюстрации для docx/PDF публичной редакции
	python3 scripts/charts.py
public:           # публичная редакция для the-tenge.kz: HTML, docx, PDF, метаданные
	python3 scripts/build_public.py
html:
	python3 scripts/build_public.py --html-only
test-public:      # автотест интерактивности (нужен playwright и chromium)
	python3 scripts/test_public_html.py
manifest:
	python3 scripts/manifest.py
snapshot:
	bash scripts/snapshot_edition.sh
all: check build charts public test-public snapshot
