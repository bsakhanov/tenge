.PHONY: check lint build manifest snapshot
check:
	python3 scripts/check.py
lint:
	python3 scripts/lint.py
build:
	python3 scripts/make.py
manifest:
	python3 scripts/manifest.py
snapshot: build
	bash scripts/snapshot_edition.sh
