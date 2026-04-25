"""Seq-compatible structured logger.

Logs to stdout in JSON so any container agent can scrape it; if SEQ_URL + SEQ_API_KEY
are set, the same records are POSTed to Seq's /api/events/raw in the background.

Logan reads from Seq — keep the shape stable (Application, Level, MessageTemplate).
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
from datetime import datetime, timezone
from typing import Any

import httpx

_SEQ_URL = os.environ.get("SEQ_URL", "").rstrip("/")
_SEQ_API_KEY = os.environ.get("SEQ_API_KEY", "")
_APP = os.environ.get("APP_NAME", "swarm-lab")

_q: "queue.Queue[dict[str, Any]]" = queue.Queue(maxsize=1000)


def _record(level: str, template: str, **props: Any) -> dict[str, Any]:
    return {
        "@t": datetime.now(timezone.utc).isoformat(),
        "@l": level.upper(),
        "@mt": template,
        "Application": _APP,
        **props,
    }


def _worker() -> None:
    if not (_SEQ_URL and _SEQ_API_KEY):
        return
    with httpx.Client(timeout=5.0) as client:
        while True:
            batch: list[dict[str, Any]] = []
            rec = _q.get()
            batch.append(rec)
            try:
                while len(batch) < 20:
                    batch.append(_q.get_nowait())
            except queue.Empty:
                pass
            try:
                client.post(
                    f"{_SEQ_URL}/api/events/raw?clef",
                    headers={"X-Seq-ApiKey": _SEQ_API_KEY,
                             "Content-Type": "application/vnd.serilog.clef"},
                    content="\n".join(json.dumps(r) for r in batch).encode(),
                )
            except Exception as e:  # noqa: BLE001
                logging.getLogger(__name__).warning("Seq POST failed: %s", e)


_thread = threading.Thread(target=_worker, daemon=True)
_thread.start()


def log(level: str, template: str, **props: Any) -> None:
    rec = _record(level, template, **props)
    print(json.dumps(rec), flush=True)
    try:
        _q.put_nowait(rec)
    except queue.Full:
        pass


def info(template: str, **props: Any) -> None: log("info", template, **props)
def warn(template: str, **props: Any) -> None: log("warning", template, **props)
def error(template: str, **props: Any) -> None: log("error", template, **props)
