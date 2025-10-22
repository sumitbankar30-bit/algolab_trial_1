import pandas as pd


class MACrossover:
    """Long when fast MA > slow MA; otherwise flat."""

    def __init__(self, fast: int = 10, slow: int = 20) -> None:
        if fast >= slow:
            raise ValueError("fast must be < slow")
        self.fast = fast
        self.slow = slow

    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Accepts a DataFrame with either:
          - 'time' (ISO-like) or
          - 'date' (YYYY-MM-DD or DD-MM-YYYY)
        and a 'close' column.

        Returns a DataFrame indexed by timestamp with columns:
        ['close', 'sma_short', 'sma_long', 'signal'].
        """
        out = df.copy()

        if "time" in out.columns:
            idx = pd.to_datetime(out["time"], utc=True, errors="coerce")
            out = out.assign(_t=idx).dropna(subset=["_t"]).set_index("_t").drop(columns=["time"])
        elif "date" in out.columns:
            # handle both YYYY-MM-DD and DD-MM-YYYY
            idx = pd.to_datetime(out["date"], utc=True, errors="coerce", dayfirst=True)
            out = out.assign(_t=idx).dropna(subset=["_t"]).set_index("_t").drop(columns=["date"])

        out["close"] = pd.to_numeric(out["close"], errors="coerce")
        out = out.dropna(subset=["close"]).sort_index()

        out["sma_short"] = out["close"].rolling(self.fast, min_periods=self.fast).mean()
        out["sma_long"] = out["close"].rolling(self.slow, min_periods=self.slow).mean()
        out["signal"] = (out["sma_short"] > out["sma_long"]).astype(int)

        return out.dropna(subset=["sma_short", "sma_long"])

    # Backwards-compat for tests: same as signals(), but returns a flat table with a 'date' column.
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # compute signals as before
        res = self.signals(df).reset_index().rename(columns={"_t": "time"})

        # make 'date' a datetime64[ns] (tz-naive) so .isoformat() works in tests
        dt = pd.to_datetime(res["time"], utc=True, errors="coerce")
        res["date"] = dt.dt.tz_localize(None)  # drop timezone, keep as Timestamp dtype

        # canonical column order expected by runner/tests
        cols = [c for c in ["date", "close", "sma_short", "sma_long", "signal"] if c in res.columns]
        return res[cols]


# Alias expected by tests
MovingAverageCrossover = MACrossover
