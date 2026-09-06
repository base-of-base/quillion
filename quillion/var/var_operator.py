"""VarOperator class - wrapper for variable operations."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..components.base import Component
    from .var import Var

import operator

from .computed_value import ComputedValue, _create_computed
from .reactive_expression import ReactiveExpression

__all__ = ["VarOperator"]


class VarOperator(ReactiveExpression):
    """Wrapper for variable operations that supports both reactive observation and assignment."""
    __slots__ = ("_computed", "_op_func", "_other", "_var")

    def __init__(self, var: Var, op_func: Callable, other: Any) -> None:
        self._var = var  # type: ignore
        self._op_func = op_func
        self._other = other
        self._computed = _create_computed(op_func, var, other)  # type: ignore

    @property
    def value(self) -> Any:
        """Get the computed value of this operation."""
        return self._computed.value

    @property
    def _dependencies(self) -> list:
        """Return the dependencies of this operation."""
        return self._computed._dependencies  # type: ignore

    def observe(self, comp: Component, cb: Callable) -> None:
        """Register an observer for changes to this operation's value."""
        self._computed.observe(comp, cb)

    def __call__(self, *args, **kwargs) -> None:
        """Apply the operation and assign the result back to the variable."""
        new_value = self._op_func(self._var.value, self._other)  # type: ignore
        self._var.set(new_value)  # type: ignore

    def __eq__(self, other: object) -> ComputedValue:
        """Equality comparison with computed value."""
        from .computed_value import _create_computed
        return _create_computed(operator.eq, self._computed, other)  # type: ignore

    def __ne__(self, other: object) -> ComputedValue:
        """Inequality comparison with computed value."""
        from .computed_value import _create_computed
        return _create_computed(operator.ne, self._computed, other)  # type: ignore

    def __lt__(self, other: Any) -> ComputedValue:
        """Less than comparison with computed value."""
        from .computed_value import _create_computed
        return _create_computed(operator.lt, self._computed, other)  # type: ignore

    def __le__(self, other: Any) -> ComputedValue:
        """Less than or equal comparison with computed value."""
        from .computed_value import _create_computed
        return _create_computed(operator.le, self._computed, other)  # type: ignore

    def __gt__(self, other: Any) -> ComputedValue:
        """Greater than comparison with computed value."""
        from .computed_value import _create_computed
        return _create_computed(operator.gt, self._computed, other)  # type: ignore

    def __ge__(self, other: Any) -> ComputedValue:
        """Greater than or equal comparison with computed value."""
        from .computed_value import _create_computed
        return _create_computed(operator.ge, self._computed, other)  # type: ignore

    def __str__(self) -> str:
        """String representation of the computed value."""
        return str(self.value)

    def __format__(self, format_spec: str) -> str:
        """Format the computed value."""
        return format(self.value, format_spec)

    def __bool__(self) -> bool:
        """Boolean conversion."""
        return bool(self.value)

    def __int__(self) -> int:
        """Integer conversion."""
        return int(self.value)

    def __float__(self) -> float:
        """Float conversion."""
        return float(self.value)

    def __repr__(self) -> str:
        """Detailed representation of the operator."""
        return f"VarOperator({self._var!r}, {self._op_func.__name__}, {self._other!r})"
