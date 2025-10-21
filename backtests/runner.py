from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from algos.ma_crossover import MovingAverageCrossover
from utils.config import AppConfig
from utils.logging import get_logger


def _bps_to_frac(bps: float) -> float:
    return bps / 10000.0


def load_prices(raw_path: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_path, parse_dates=["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def build_features(df: pd.DataFrame, short: int, long: int) -> pd.DataFrame:
    strat = MovingAverageCrossover(short, long)
    return strat.generate_signals(df)


def run_backtest(cfg: AppConfig) -> dict:
    logger = get_logger("backtest", cfg.io.log_dir)

    raw_file = Path(cfg.data_paths.raw) / "prices_sample.csv"
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw prices not found: {raw_file}")

    logger.info("Loading prices from %s", raw_file)
    prices = load_prices(raw_file)

    # Trim by date window if provided
    if cfg.backtest.start:
        prices = prices[prices["date"] >= pd.Timestamp(cfg.backtest.start)]
    if cfg.backtest.end:
        prices = prices[prices["date"] <= pd.Timestamp(cfg.backtest.end)]
    prices = prices.reset_index(drop=True)

    logger.info("Building features short=%s long=%s", cfg.features.sma_short, cfg.features.sma_long)
    df = build_features(prices, cfg.features.sma_short, cfg.features.sma_long)

    # Compute returns
    df["return"] = df["close"].pct_change().fillna(0.0)
    fee = _bps_to_frac(cfg.backtest.fee_bps)
    slippage = _bps_to_frac(cfg.backtest.slippage_bps)

    # Strategy returns: apply position (signal) to next-day return, subtract costs on signal changes
    df["position"] = df["signal"].shift(1).fillna(0)  # enter at next bar
    df["trade"] = df["signal"].diff().abs().fillna(0)
    cost_per_trade = fee + slippage
    df["strategy_return"] = df["position"] * df["return"] - df["trade"] * cost_per_trade

    equity = (1 + df["strategy_return"]).cumprod() * cfg.backtest.initial_capital
    total_return = equity.iloc[-1] / cfg.backtest.initial_capital - 1.0

    # Daily sharpe (no risk-free), simple
    if df["strategy_return"].std(ddof=0) > 0:
        sharpe = (df["strategy_return"].mean() / df["strategy_return"].std(ddof=0)) * np.sqrt(252)
    else:
        sharpe = 0.0

    win_rate = (df["strategy_return"] > 0).mean()

    summary = {
        "observations": len(df),
        "total_return": float(total_return),
        "sharpe_annualized": float(sharpe),
        "win_rate": float(win_rate),
        "final_equity": float(equity.iloc[-1]),
        "start": df["date"].iloc[0].isoformat(),
        "end": df["date"].iloc[-1].isoformat(),
    }

    out_path = Path(cfg.io.report_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2))
    logger.info("Wrote backtest summary to %s", out_path)

    return summary
