from __future__ import annotations

import pandas as pd


class Strategy:
    """Base class for trading strategies producing a 'signal' column."""

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError
