"""
TwoWayBindingElement: base for components that sync with a Var.
"""

from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING

from .. import _context as ctx
from .base import Component, UIComponentMeta

if TYPE_CHECKING:
    from ..var import Var
    from ..session import Session


class TwoWayComponentMeta(UIComponentMeta):
    """Registers subclasses in the TWO_WAY_REGISTRY."""

    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        if name != "TwoWayBindingElement" and issubclass(cls, TwoWayBindingElement):
            alias = getattr(cls, "_component_alias", None) or name.lower().removesuffix("component")
            ctx.TWO_WAY_REGISTRY[alias] = cls
            if getattr(cls, "_is_default", False):
                ctx.default_two_way_class = cls
        return cls


class TwoWayBindingElement(Component, metaclass=TwoWayComponentMeta):
    _bind_var: Optional["Var"]
    _updating_from_var: bool

    def __init__(self, bind_var: Optional["Var"] = None, **kwargs):
        self._bind_var           = bind_var
        self._updating_from_var  = False
        super().__init__(**kwargs)

    def _post_init(self) -> None:
        if self._bind_var:
            self._bind_var.observe(self, lambda c, v, s: self._update_from_var(s))

    def _update_from_var(self, session: "Session") -> None:
        if not self._updating_from_var:
            self._updating_from_var = True
            try:
                if session:
                    session.updater.schedule_update(self)
            finally:
                self._updating_from_var = False

    def get_current_value(self) -> str:
        return str(self._bind_var.value) if self._bind_var else ""

    def update_var_from_event(self, event_value: str) -> None:
        if not self._bind_var:
            return
        cur = self._bind_var.value
        if isinstance(cur, int):
            event_value = int(event_value) if event_value else 0 # type: ignore
        elif isinstance(cur, float):
            event_value = float(event_value) if event_value else 0.0 # type: ignore
        elif isinstance(cur, bool):
            event_value = event_value.lower() in ("true", "1", "yes", "on") # type: ignore
        self._bind_var.value = event_value
