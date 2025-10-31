# utils/paths.py
from __future__ import annotations

from os import PathLike
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def repo_path(*parts: str | PathLike[str]) -> Path:
    """Join parts to the repo root, accepting str or Path-like inputs."""
    return ROOT.joinpath(*(str(p) for p in parts))
