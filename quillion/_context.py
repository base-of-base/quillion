"""
Global runtime context shared across the package.

Keeping these in one place avoids circular-import tangles.
"""

from __future__ import annotations
from contextvars import ContextVar
from typing import TYPE_CHECKING, Dict, Optional, Type

if TYPE_CHECKING:
    from .app import App
    from .session import Session
    from .components.two_way import TwoWayBindingElement

quillion_app: Optional["App"] = None

current_session: ContextVar[Optional["Session"]] = ContextVar(
    "current_session", default=None
)

TWO_WAY_REGISTRY: Dict[str, Type["TwoWayBindingElement"]] = {}

default_two_way_class: Optional[Type["TwoWayBindingElement"]] = None

VAR_NAME_REGISTRY: Dict[str, str] = {}
