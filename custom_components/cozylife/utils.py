"""Local utility helpers for the CozyLife integration."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

_PID_CACHE: dict[Path, list[dict[str, Any]]] = {}


def get_sn() -> str:
    """Return a millisecond-resolution protocol sequence number."""

    return str(time.time_ns() // 1_000_000)


def _normalise_catalog_payload(raw_payload: Any) -> list[dict[str, Any]]:
    """Extract the model list from the stored catalog structure."""

    if isinstance(raw_payload, list):
        return [item for item in raw_payload if isinstance(item, dict)]

    if isinstance(raw_payload, dict):
        info = raw_payload.get("info")
        if isinstance(info, dict):
            nested_list = info.get("list")
            if isinstance(nested_list, list):
                return [item for item in nested_list if isinstance(item, dict)]

    _LOGGER.info("Local device model cache structure is not as expected")
    return []


def get_pid_list(model_path: Path, lang: str = "en") -> list[dict[str, Any]]:
    """Load and cache the CozyLife model catalog snapshot."""

    del lang  # The checked-in snapshot is language-agnostic for runtime use.

    resolved_path = model_path.resolve()
    if resolved_path in _PID_CACHE:
        return _PID_CACHE[resolved_path]

    try:
        raw_text = resolved_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        _LOGGER.error("Local device model cache not found: %s", resolved_path)
        return []
    except OSError as err:
        _LOGGER.error(
            "Unable to read local device model cache %s: %s",
            resolved_path,
            err,
        )
        return []

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as err:
        _LOGGER.error(
            "Error decoding local device model cache %s: %s",
            resolved_path,
            err,
        )
        return []

    model_list = _normalise_catalog_payload(payload)
    _PID_CACHE[resolved_path] = model_list
    return model_list
