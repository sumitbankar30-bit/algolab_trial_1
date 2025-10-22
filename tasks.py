#!/usr/bin/env python
from __future__ import annotations

import pandas as pd
import argparse
import json
from pathlib import Path

import pandas as pd  # <-- NEW: so we can read features.csv

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

    # Locate features file
    features_base = Path(cfg.data_paths.features)
    # optional override: cfg.io.features_file (if you add it in YAML later)
    features_path = Path(getattr(cfg.io, "features_file", features_base / "features.csv"))

    print("[DEBUG] Using features:", features_path)
    df = None
    if features_path.exists():
        df = pd.read_csv(features_path)
        print("[DEBUG] Head:\n", df.head().to_string())
    else:
        print("[DEBUG] Features file does not exist")

    # --- SIGNAL-AWARE summary using features.csv (your snippet)
    summary = {"total_return": 0.0, "sharpe_annualized": 0.0}
    try:
        import numpy as np

        if df is not None and not df.empty:
            # normalize columns
            df.columns = [str(c).strip().lower() for c in df.columns]

            # pick a time column (optional, for sorting)
            tcol = None
            for c in ("time", "date", "timestamp", "datetime", "ts"):
                if c in df.columns:
                    tcol = c; break
            if tcol:
                dt = pd.to_datetime(df[tcol], utc=True, errors="coerce", dayfirst=True)
                df = df.assign(_t=dt).dropna(subset=["_t"]).sort_values("_t").drop(columns=["_t"])

            # choose a price column
            price_col = None
            for c in ("close", "price", "feature", "value"):
                if c in df.columns:
                    price_col = c; break
            if not price_col:
                raise ValueError("No price-like column found (need close/price/feature/value).")
            df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

            # get or build a signal: prefer existing 'signal', else MA crossover
            if "signal" in df.columns:
                sig = pd.to_numeric(df["signal"], errors="coerce").fillna(0).clip(-1, 1).astype(int)
            else:
                # fallback crossover on price
                fast, slow = 10, 30
                ma_f = df[price_col].rolling(fast, min_periods=fast).mean()
                ma_s = df[price_col].rolling(slow, min_periods=slow).mean()
                sig = (ma_f > ma_s).astype(int)
            df = df.dropna(subset=[price_col])
            df["signal"] = sig
            print("[DEBUG] rows:", len(df),
               "signal_counts:", df["signal"].value_counts(dropna=False).to_dict(),
               "entries:", int((df["signal"].diff() == 1).sum()),
               "exits:", int((df["signal"].diff() == -1).sum()))


            # simple long/flat with 1 bps fee
            fee = 1.0 / 10_000.0
            cash, pos = 100_000.0, 0.0
            equity = []
            for price, s in zip(df[price_col].values, df["signal"].values):
                if s == 0 and pos > 0:  # exit
                    cash += pos * price; cash -= pos * price * fee; pos = 0.0
                if s == 1 and pos == 0.0:  # enter
                    units = cash / price; cash -= units * price; cash -= units * price * fee; pos = units
                equity.append(cash + pos * price)

            eq = np.array(equity)
            rets = np.diff(eq) / eq[:-1] if len(eq) > 1 else np.array([])
            total_return = float(eq[-1] / 100_000.0 - 1) if len(eq) else 0.0
            sharpe = float((rets.mean() / (rets.std() + 1e-12)) * np.sqrt(252)) if len(rets) else 0.0
            summary = {"total_return": total_return, "sharpe_annualized": sharpe}
    except Exception as e:
        print("[DEBUG] Backtest calc error:", repr(e))

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
