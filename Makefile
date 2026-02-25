PYTHON ?= python

.PHONY: install venv test lint smoke report-grad-overlay

venv:
	$(PYTHON) -m venv .venv
	.venv\\Scripts\\python -m pip install --upgrade pip
	.venv\\Scripts\\python -m pip install -r requirements.txt

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests

smoke:
	powershell -ExecutionPolicy Bypass -File scripts/smoke_run.ps1

report-grad-overlay:
	$(PYTHON) scripts/make_grad_variance_overlay.py
