#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from utils.config import load_config


def ensure_dirs(*paths: Path | str) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def _resolve_features_path(cfg: Any) -> Path:
    features_base = Path(cfg.data_paths.features)
    return Path(getattr(cfg.io, "features_file", features_base / "features.csv"))


def _read_features(path: Path) -> pd.DataFrame:
    if not path.exists():
        print("[DEBUG] Features file does not exist:", path)
        return pd.DataFrame()
    df = pd.read_csv(path)
    print("[DEBUG] Using features:", path)
    print("[DEBUG] Head:\n", df.head().to_string())
    return df


def _sort_by_time(df: pd.DataFrame) -> pd.DataFrame:
    # normalize columns
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    # pick a time column and sort; handle DD-MM-YYYY via dayfirst=True
    tcol: str | None = next(
        (c for c in ("time", "date", "timestamp", "datetime", "ts") if c in df.columns),
        None,
    )
    if tcol:
        dt = pd.to_datetime(df[tcol], utc=True, errors="coerce", dayfirst=True)
        df = df.assign(_t=dt).dropna(subset=["_t"]).sort_values("_t").drop(columns=["_t"])
    return df


def _select_price_col(df: pd.DataFrame) -> str:
    for c in ("close", "price", "feature", "value"):
        if c in df.columns:
            return c
    msg = "No price-like column found (need close/price/feature/value)."
    raise ValueError(msg)


def _build_signal(df: pd.DataFrame, price_col: str) -> pd.Series:
    if "signal" in df.columns:
        return pd.to_numeric(df["signal"], errors="coerce").fillna(0).clip(-1, 1).astype(int)
    # fallback: MA crossover on price
    fast, slow = 10, 30
    ma_f = df[price_col].rolling(fast, min_periods=fast).mean()
    ma_s = df[price_col].rolling(slow, min_periods=slow).mean()
    return (ma_f > ma_s).astype(int)


def _run_long_flat(
    df: pd.DataFrame,
    price_col: str,
    fee_bps: float = 1.0,
    initial_cash: float = 100_000.0,
) -> dict:
    fee = fee_bps / 10_000.0
    cash = initial_cash
    pos = 0.0
    equity: list[float] = []

    for price, s in zip(df[price_col].values, df["signal"].values):
        if s == 0 and pos > 0:
            cash += pos * price
            cash -= pos * price * fee
            pos = 0.0
        if s == 1 and pos == 0.0:
            units = cash / price
            cash -= units * price
            cash -= units * price * fee
            pos = units
        equity.append(cash + pos * price)

    eq = np.array(equity, dtype=float)
    rets = np.diff(eq) / eq[:-1] if len(eq) > 1 else np.array([], dtype=float)
    total_return = float(eq[-1] / initial_cash - 1.0) if len(eq) else 0.0
    sharpe = float((rets.mean() / (rets.std() + 1e-12)) * np.sqrt(252)) if rets.size else 0.0
    return {"total_return": total_return, "sharpe_annualized": sharpe}


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
    # minimal placeholder so step is observable (won't be used by backtest once real features exist)
    features_csv = features_dir / "features.csv"
    if not features_csv.exists():
        features_csv.write_text("ts,feature\n0,0.0\n", encoding="utf-8")
    return 0


def cmd_backtest(config_path: str) -> int:
    cfg = load_config(config_path)
    report_path = Path(cfg.io.report_path)
    ensure_dirs(report_path.parent, cfg.io.log_dir)

    features_path = _resolve_features_path(cfg)
    df = _read_features(features_path)
    if df.empty:
        summary = {"total_return": 0.0, "sharpe_annualized": 0.0}
        report_path.write_text(json.dumps(summary), encoding="utf-8")
        return 0

    df = _sort_by_time(df)

    price_col = _select_price_col(df)
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    df = df.dropna(subset=[price_col])

    df["signal"] = _build_signal(df, price_col)
    # helpful debug
    print(
        "[DEBUG] rows:",
        len(df),
        "signal_counts:",
        df["signal"].value_counts(dropna=False).to_dict(),
        "entries:",
        int((df["signal"].diff() == 1).sum()),
        "exits:",
        int((df["signal"].diff() == -1).sum()),
    )

    summary = _run_long_flat(
        df,
        price_col,
        fee_bps=float(getattr(cfg.backtest, "fee_bps", 1.0)),
        initial_cash=float(getattr(cfg.backtest, "initial_capital", 100_000)),
    )
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
