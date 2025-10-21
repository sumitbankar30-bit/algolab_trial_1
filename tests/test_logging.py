from pathlib import Path

from utils.logging import get_logger


def test_logging_creates_file(tmp_path: Path) -> None:
    logger = get_logger("test", tmp_path)
    files = list(tmp_path.glob("run_*.log"))
    assert files, "No log file created"
    logger.info("hello")
