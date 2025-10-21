.PHONY: help install lint format typecheck test ingest features backtest

help:
	@echo "Targets:"
	@echo "  install   - pip install project and dev tools"
	@echo "  lint      - ruff"
	@echo "  format    - black"
	@echo "  typecheck - mypy"
	@echo "  test      - pytest"
	@echo "  ingest    - run data ingestion"
	@echo "  features  - build features"
	@echo "  backtest  - run backtest"

install:
	python -m pip install --upgrade pip
	pip install -e .[dev]
	pre-commit install

lint:
	ruff check .

format:
	black .

typecheck:
	mypy .

test:
	pytest -q

ingest:
	python tasks.py ingest --config configs/default.yaml

features:
	python tasks.py features --config configs/default.yaml

backtest:
	python tasks.py backtest --config configs/default.yaml
