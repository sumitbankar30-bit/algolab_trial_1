from __future__ import annotations

import argparse
import shutil

from backtests.runner import build_features, load_prices, run_backtest
from utils.config import AppConfig, load_config
from utils.paths import repo_path


def ingest(cfg: AppConfig) -> None:
    """Copy raw sample CSV to staging; in real life, validate/download/etc."""
    raw = repo_path(str(cfg.data_paths.raw))
    staging = repo_path(str(cfg.data_paths.staging))
 #   out_dir = repo_path(str(cfg.data_paths.features))
    staging.mkdir(parents=True, exist_ok=True)
    src = raw / "prices_sample.csv"
    dst = staging / "prices_sample.csv"
    shutil.copy2(src, dst)
    print(f"[ingest] Copied {src} -> {dst}")


def features(cfg: AppConfig) -> None:
    """Build MA features and save to data/features."""
    staging = repo_path(cfg.data_paths.staging) / "prices_sample.csv"
    if not staging.exists():
        raise FileNotFoundError("Staging data not found; run `make ingest` first.")
    df = load_prices(staging)
    df_feat = build_features(df, cfg.features.sma_short, cfg.features.sma_long)
    out_dir = repo_path(cfg.data_paths.features)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "features_sample.csv"
    df_feat.to_csv(out, index=False)
    print(f"[features] Wrote features to {out}")


def backtest(cfg: AppConfig) -> None:
    """Run toy backtest and write a JSON report."""
    summary = run_backtest(cfg)
    print("[backtest] Summary:", summary)


def main() -> None:
    ap = argparse.ArgumentParser(description="algolab tasks")
    ap.add_argument("command", choices=["ingest", "features", "backtest"])
    ap.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to YAML config file",
    )
    args = ap.parse_args()
    cfg = load_config(args.config)
    if args.command == "ingest":
        ingest(cfg)
    elif args.command == "features":
        features(cfg)
    elif args.command == "backtest":
        backtest(cfg)


if __name__ == "__main__":
    main()
