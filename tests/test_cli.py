import subprocess
import sys


def test_cli_ingest_and_features_and_backtest() -> None:
    # Run ingest
    r1 = subprocess.run(
        [sys.executable, "tasks.py", "ingest", "--config", "configs/default.yaml"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert r1.returncode == 0, r1.stderr

    # Run features
    r2 = subprocess.run(
        [sys.executable, "tasks.py", "features", "--config", "configs/default.yaml"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert r2.returncode == 0, r2.stderr

    # Run backtest
    r3 = subprocess.run(
        [sys.executable, "tasks.py", "backtest", "--config", "configs/default.yaml"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert r3.returncode == 0, r3.stderr
