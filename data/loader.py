from pathlib import Path
import pandas as pd

def load_prices(path: Path) -> pd.DataFrame:
    """
    CSV with columns: time, close
    Parses time to UTC, sets it as index, sorts ascending.
    """
    df = pd.read_csv(path)
    if "time" not in df or "close" not in df:
        raise ValueError("CSV must contain 'time' and 'close' columns")
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
    df = df.dropna(subset=["time", "close"]).set_index("time").sort_index()
    return df[["close"]]
