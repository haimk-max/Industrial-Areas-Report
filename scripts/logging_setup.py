"""Structured logging for all scripts. JSONL output to logs/run_<timestamp>.jsonl."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if hasattr(record, "fields") and isinstance(record.fields, dict):
            payload.update(record.fields)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(script_name: str, logs_dir: Path | str = "logs") -> logging.Logger:
    logs_path = Path(logs_dir)
    logs_path.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_file = logs_path / f"{script_name}_{ts}.jsonl"

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(JsonFormatter())
    root.addHandler(file_handler)

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(logging.Formatter("%(levelname)s | %(message)s"))
    root.addHandler(console)

    logger = logging.getLogger(script_name)
    logger.info(f"Logging initialized → {log_file}")
    return logger


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    """Helper for structured event logging with arbitrary fields."""
    logger.info(event, extra={"fields": {"event": event, **fields}})
