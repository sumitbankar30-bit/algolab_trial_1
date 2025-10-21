# Contributing

## Branching
- `main` stays green; create feature branches: `feat/…`, `fix/…`, `chore/…`.

## Commits
- Use Conventional Commits: `feat: …`, `fix: …`, `docs: …`, `chore: …`.
- Small, focused commits. Tests for behavior changes.

## Pre-commit
- Run `pre-commit install` once. Hooks will auto-run on commit.

## Quality gates
- `ruff` (lint), `black` (format), `mypy` (types), `pytest` (tests). CI runs them all.
- Keep functions small and pure. Push state to the edges (IO in utils/backtests).

## Tests
- Write tests for configs, paths, logging, and any new algorithm behavior.
- Use parametrization for config matrices and toy datasets.
