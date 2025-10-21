from pathlib import Path


def test_repo_paths_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    for p in [
        "algos",
        "backtests",
        "configs",
        "data/raw",
        "data/staging",
        "data/features",
        "utils",
    ]:
        assert (root / p).exists(), f"Missing path: {p}"
