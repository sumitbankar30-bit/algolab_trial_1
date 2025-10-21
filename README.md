# algolab — Phase 0 scaffold

A minimal, reproducible lab for algorithmic trading research and backtesting.

## Quickstart

```bash
# 1) Create & activate a virtualenv (examples below)
python -m venv .venv
source .venv/bin/activate  # (Windows) .venv\Scripts\activate

# 2) Install
pip install -e .[dev]

# 3) Install pre-commit hooks
pre-commit install

# 4) Smoke run
make ingest
make features
make backtest
```

### What these do
- `make ingest`: copies/validates raw data into `data/staging`.
- `make features`: builds simple features into `data/features`.
- `make backtest`: runs a toy MA-crossover backtest and writes a summary to `reports/`.

## Repo layout

```text
algolab/
  data/{raw,staging,features}
  algos/
  backtests/
  configs/
  tests/
  reports/
  notebooks/
  utils/
```

## Configuration

See `configs/default.yaml`. Configuration is validated with Pydantic. You can create your own
file and pass it via `--config` to the CLI (e.g., `python tasks.py backtest --config configs/default.yaml`).

## Development

```bash
# Lint + format + types + tests
ruff check .
black .
mypy .
pytest
```

Or just rely on CI and pre-commit.

## Notes
- This is a pedagogical skeleton: safe defaults, simple patterns, and small pure functions.
- Upgrade to experiment tracking / DVC / Docker later without reshuffling the layout.
