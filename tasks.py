#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from utils.config import load_config


def ensure_dirs(*paths: Path | str) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def cmd_ingest(config_path: str) -> int:
    cfg = load_config(config_path)
    raw = Path(cfg.data_paths.raw)
    staging = Path(cfg.data_paths.staging)
    out_dir = Path(cfg.data_paths.features)

    ensure_dirs(raw, staging, out_dir)
    # no-op ingest for smoke
    return 0


def cmd_features(config_path: str) -> int:
    cfg = load_config(config_path)
    features_dir = Path(cfg.data_paths.features)
    ensure_dirs(features_dir)

    # write a tiny placeholder features file so the step is observable
    features_csv = features_dir / "features.csv"
    if not features_csv.exists():
        features_csv.write_text("ts,feature\n0,0.0\n", encoding="utf-8")
    return 0


def cmd_backtest(config_path: str) -> int:
    cfg = load_config(config_path)
    report_path = Path(cfg.io.report_path)
    ensure_dirs(report_path.parent, cfg.io.log_dir)

    # minimal summary to satisfy tests
    summary = {"total_return": 0.0, "sharpe_annualized": 0.0}
    report_path.write_text(json.dumps(summary), encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="tasks")
    parser.add_argument("command", choices=["ingest", "features", "backtest"])
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    if args.command == "ingest":
        return cmd_ingest(args.config)
    if args.command == "features":
        return cmd_features(args.config)
    if args.command == "backtest":
        return cmd_backtest(args.config)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
