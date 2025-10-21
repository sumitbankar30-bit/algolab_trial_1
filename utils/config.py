from __future__ import annotations
import yaml  # type: ignore[import-untyped]
from pathlib import Path
from typing import Mapping
from pydantic import BaseModel, Field, field_validator


class DataPaths(BaseModel):
    raw: Path
    staging: Path
    features: Path


class FeatureConfig(BaseModel):
    sma_short: int = Field(10, ge=1)
    sma_long: int = Field(30, ge=2)

    @field_validator("sma_long")
    @classmethod
    def _check_order(cls, v, info):
        # Ensure long > short if both present
        short = info.data.get("sma_short", 10)
        if v <= short:
            raise ValueError("sma_long must be > sma_short")
        return v


class BacktestConfig(BaseModel):
    symbol: str
    initial_capital: float = Field(100000, ge=0)
    fee_bps: float = Field(0.0, ge=0)
    slippage_bps: float = Field(0.0, ge=0)
    start: str | None = None
    end: str | None = None


class IOConfig(BaseModel):
    report_path: Path = Path("reports/backtest_summary.json")
    log_dir: Path = Path("logs")


class AppConfig(BaseModel):
    data_paths: DataPaths
    features: FeatureConfig
    backtest: BacktestConfig
    io: IOConfig


def load_config(path: str | Path) -> AppConfig:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return AppConfig.model_validate(data)
