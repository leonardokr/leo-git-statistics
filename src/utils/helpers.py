#!/usr/bin/python3
"""Utility helper functions."""

from typing import Optional


def to_bool(val: Optional[str], default: bool = False) -> bool:
    """Convert a string value to boolean with a default fallback."""
    if val is None:
        return default
    return str(val).strip().lower() == "true"
