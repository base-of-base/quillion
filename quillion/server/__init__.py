"""Server package."""

from __future__ import annotations

from .handler import (
    StaticFileHandler,
    http_handler,
    is_static_path,
)

__all__ = [
    "StaticFileHandler",
    "http_handler",
    "is_static_path",
]
