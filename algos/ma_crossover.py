import pandas as pd

class MACrossover:
    """Long when fast MA > slow MA; otherwise flat."""
    def __init__(self, fast: int = 10, slow: int = 20) -> None:
        if fast >= slow:
            raise ValueError("fast must be < slow")
        self.fast, self.slow = fast, slow

    def signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # expects df indexed by time with a 'close' column
        out = df.copy()
        out["ma_fast"] = out["close"].rolling(self.fast, min_periods=self.fast).mean()
        out["ma_slow"] = out["close"].rolling(self.slow, min_periods=self.slow).mean()
        out["signal"]  = (out["ma_fast"] > out["ma_slow"]).astype(int)  # 1 long, 0 flat
        return out.dropna()
