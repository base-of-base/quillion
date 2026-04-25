"""FormattedVar class - reactively formatted variable representation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .var import Var
    from ..components.base import Component

__all__ = ["FormattedVar"]


class FormattedVar(str):
    """Reactively formatted variable representation (string with subscription)."""
    def __new__(cls, initial_value: str, var: Var, format_spec: str):
        instance = super().__new__(cls, initial_value)
        instance._var = var  # type: ignore
        instance._format_spec = format_spec  # type: ignore
        return instance

    def __str__(self) -> str:
        """Format the variable's current value."""
        try:
            return format(self._var.value, self._format_spec)  # type: ignore
        except (ValueError, TypeError):
            return str(self._var.value)  # type: ignore

    def observe(self, comp: Component, cb: Callable) -> None:
        """Register an observer for changes to the underlying variable."""
        self._var.observe(comp, cb)  # type: ignore
