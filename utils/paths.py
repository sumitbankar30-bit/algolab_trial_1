# utils/paths.py
from __future__ import annotations
from pathlib import Path
from os import PathLike
from typing import Union

ROOT = Path(__file__).resolve().parents[1]

def repo_path(*parts: Union[str, PathLike[str]]) -> Path:
    # Accept str or Path/PathLike; normalize to strings
    return ROOT.joinpath(*(str(p) for p in parts))
