"""
Centralised logging setup using loguru.
Import `logger` from this module everywhere — never use print().
"""
import sys
from pathlib import Path
from loguru import logger

_configured = False


def setup_logger(log_dir: Path = None, level: str = "INFO") -> None:
    global _configured
    if _configured:
        return

    logger.remove()  # remove default handler

    # Console — coloured, human-friendly
    logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # File — full details, rotates daily, 7-day retention
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        logger.add(
            log_dir / "pipeline_{time:YYYY-MM-DD}.log",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} — {message}",
            rotation="00:00",
            retention="7 days",
            compression="zip",
        )

    _configured = True


# Auto-configure when imported
from config.settings import LOGS_DIR
setup_logger(log_dir=LOGS_DIR)

__all__ = ["logger"]
