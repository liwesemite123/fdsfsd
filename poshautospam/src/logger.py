import logging
from datetime import datetime, timezone
from pathlib import Path


def setup_logging() -> None:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = logs_dir / f"backend_run_{timestamp}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),
        ],
    )

    logging.info("Logging initialized: %s", log_filename)
