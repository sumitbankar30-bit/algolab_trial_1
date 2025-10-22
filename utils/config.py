# utils/config.py
from __future__ import annotations

from pathlib import Path  # stdlib

import yaml
from pydantic import BaseModel, Field, ValidationInfo, field_validator  # third-party


class DataPaths(BaseModel):
    raw: Path
    staging: Path
    features: Path


class FeatureConfig(BaseModel):
    sma_short: int = Field(10, ge=1)
    sma_long: int = Field(30, ge=2)

    @field_validator("sma_long")
    @classmethod
    def _check_order(cls, v: int, info: ValidationInfo) -> int:
        """Ensure sma_long > sma_short (Pydantic v2 style)."""
        short = info.data.get("sma_short", 10)
        try:
            short_int = int(short) if short is not None else 10
        except (TypeError, ValueError):
            short_int = 10
        if v <= short_int:
            raise ValueError("sma_long must be > sma_short")
        return v


class BacktestConfig(BaseModel):
    symbol: str
    initial_capital: float = Field(100_000, ge=0)
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
    """Read YAML and validate into AppConfig (empty/missing file -> {} defaults)."""
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}
    if data is None:
        data = {}
    return AppConfig.model_validate(data)
