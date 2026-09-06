"""
Global runtime context shared across the package.

Keeping these in one place avoids circular-import tangles.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .app import App
    from .components.two_way import TwoWayBindingElement
    from .session import Session

quillion_app: App | None = None

current_session: ContextVar[Session | None] = ContextVar(
    "current_session", default=None
)

TWO_WAY_REGISTRY: dict[str, type[TwoWayBindingElement]] = {}

default_two_way_class: type[TwoWayBindingElement] | None = None

VAR_NAME_REGISTRY: dict[str, str] = {}
