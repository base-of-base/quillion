"""FormattedVar class - reactively formatted variable representation."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from ..components.base import Component
    from .var import Var

__all__ = ["FormattedVar"]


class FormattedVar(str):
    """Reactively formatted variable representation (string with subscription)."""
    _var: Var
    _format_spec: str

    def __new__(cls, initial_value: str, var: Var, format_spec: str) -> Self:
        instance = super().__new__(cls, initial_value)
        instance._var = var
        instance._format_spec = format_spec
        return instance

    def __str__(self) -> str:
        """Format the variable's current value."""
        try:
            return format(self._var.value, self._format_spec)
        except (ValueError, TypeError):
            return str(self._var.value)

    def observe(self, comp: Component, cb: Callable[..., Any]) -> None:
        """Register an observer for changes to the underlying variable."""
        self._var.observe(comp, cb)
