"""ComputedValue class - cached reactive computation."""

from __future__ import annotations

from typing import Any, Callable, List
from weakref import WeakKeyDictionary
from ..components.base import Component
from .. import _context as ctx
from .reactive_expression import ReactiveExpression
from ._safe_op import _safe_op
from .var import Var

__all__ = ["ComputedValue", "_create_computed"]


def _create_computed(op_func: Callable, a: Any, b: Any) -> "ComputedValue":
    """Create a computed value from a binary operation."""
    deps = []
    if hasattr(a, '_dependencies'):
        deps.extend(a._dependencies)  # type: ignore
    elif isinstance(a, Var):
        deps.append(a)
    if hasattr(b, '_dependencies'):
        deps.extend(b._dependencies)  # type: ignore
    elif isinstance(b, Var):
        deps.append(b)
    seen = set()
    unique_deps = []
    for dep in deps:
        dep_id = id(dep)
        if dep_id not in seen:
            seen.add(dep_id)
            unique_deps.append(dep)
    deps = unique_deps

    def calc():
        val_a = a.value if hasattr(a, 'value') else a  # type: ignore
        val_b = b.value if hasattr(b, 'value') else b  # type: ignore
        return _safe_op(op_func, val_a, val_b)
    return ComputedValue(calc, deps)


class ComputedValue(ReactiveExpression):
    """Cached reactive computation that updates when dependencies change."""
    __slots__ = ("_func", "_dependencies", "_cached_value", "_dirty", "_observers", "__weakref__", "_unsubscribers")

    def __init__(self, func: Callable[[], Any], dependencies: List[Var]) -> None:
        """Initialize a computed value with a function and its dependencies."""
        self._func = func
        self._dependencies = dependencies
        self._cached_value = None
        self._dirty = True
        self._observers: WeakKeyDictionary[Component, List[Callable]] = WeakKeyDictionary()
        self._unsubscribers: List[Callable[[], None]] = []
        for dep in dependencies:
            unsub = dep._add_raw_callback(self._on_dep_changed)  # type: ignore
            self._unsubscribers.append(unsub)

    def _on_dep_changed(self, *args) -> None:
        """Mark as dirty when a dependency changes."""
        self._dirty = True
        session = ctx.current_session.get()
        if session is not None:
            for comp, callbacks in list(self._observers.items()):
                for cb in callbacks:
                    cb(comp, self, session)

    def observe(self, comp: Component, cb: Callable) -> None:
        """Register an observer for changes to this computed value."""
        if comp not in self._observers:
            self._observers[comp] = []
        self._observers[comp].append(cb)

    @property
    def value(self) -> Any:
        """Get the current value, recomputing if dirty."""
        if self._dirty:
            self._cached_value = self._func()
            self._dirty = False
        return self._cached_value

    def __str__(self) -> str:
        """String representation of the value."""
        return str(self.value)

    def __format__(self, format_spec: str) -> str:
        """Format the value."""
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

    def __del__(self) -> None:
        """Clean up subscriptions when destroyed."""
        for unsub in self._unsubscribers:
            unsub()
