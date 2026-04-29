from __future__ import annotations
import threading
import time
from functools import lru_cache
from typing import Callable

from mcp_server.config import config

_lock = threading.Lock()
_last_call_at: dict[str, float] = {}


def throttle(bucket: str = "osm", min_gap: float | None = None) -> None:
    gap = config.OSM_MIN_GAP_SECONDS if min_gap is None else min_gap
    with _lock:
        last = _last_call_at.get(bucket, 0.0)
        wait = gap - (time.monotonic() - last)
        if wait > 0:
            time.sleep(wait)
        _last_call_at[bucket] = time.monotonic()


def make_lru(maxsize: int | None = None) -> Callable:
    return lru_cache(maxsize=maxsize or config.GEOCODE_CACHE_SIZE)
