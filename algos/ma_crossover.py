from __future__ import annotations

import pandas as pd

from .base import Strategy


class MovingAverageCrossover(Strategy):
    def __init__(self, short: int, long: int) -> None:
        if long <= short:
            raise ValueError("long must be > short")
        self.short = short
        self.long = long

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["sma_short"] = out["close"].rolling(self.short, min_periods=self.short).mean()
        out["sma_long"] = out["close"].rolling(self.long, min_periods=self.long).mean()
        out["signal"] = 0
        out.loc[out["sma_short"] > out["sma_long"], "signal"] = 1  # long when short>long
        out["signal"] = out["signal"].ffill().fillna(0).astype(int)
        return out
