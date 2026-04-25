"""Var class - reactive variable that tracks changes."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Callable, Optional, List
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from ..components.base import Component
    from ..session import Session

from .. import _context as ctx
from .reactive_expression import ReactiveExpression
from .var_operator import VarOperator
from .formatted_var import FormattedVar

__all__ = ["Var", "var", "auto_name_vars"]


class Var(ReactiveExpression):
    """Reactive variable that tracks changes and notifies observers."""
    _key: str
    _initial: Any
    _observers: WeakKeyDictionary
    _raw_callbacks: List[Callable]
    _component_factory: Optional[Callable[..., "Component"]]
    _auto_named: bool

    def __init__(self, initial_value: Any = "") -> None:
        """Initialize a reactive variable with an optional initial value."""
        self._key = str(uuid.uuid4())
        self._initial = initial_value
        self._observers = WeakKeyDictionary()
        self._raw_callbacks = []
        self._component_factory = None
        self._auto_named = False

    def _set_stable_key(self, name: str) -> None:
        """Set a stable key for this variable based on a name."""
        if name in ctx.VAR_NAME_REGISTRY:
            self._key = ctx.VAR_NAME_REGISTRY[name]
        else:
            ctx.VAR_NAME_REGISTRY[name] = self._key
        self._auto_named = True

    @property
    def value(self) -> Any:
        """Get the current value of the variable."""
        session = ctx.current_session.get()
        if session is None:
            return self._initial
        return session.state.get_var_value(self._key, self._initial)

    @value.setter
    def value(self, new_value: Any) -> None:
        """Set the value of the variable and notify observers."""
        session = ctx.current_session.get()
        if session is None:
            raise RuntimeError("Var.value can only be set inside a session")
        session.state.set_var_value(self._key, new_value)
        self._notify(session)

    def set(self, new_value: Any) -> None:
        """Set the value of the variable."""
        self.value = new_value

    def update(self, func: Callable[[Any], Any]) -> None:
        """Update the value by applying a function to the current value."""
        self.value = func(self.value)

    def append(self, suffix: str) -> VarOperator:
        """Append a suffix to the string representation."""
        return VarOperator(self, lambda a, b: str(a) + b, suffix)  # type: ignore

    def __bool__(self) -> bool:
        """Boolean conversion."""
        return bool(self.value)

    def __len__(self) -> int:
        """Length of the value."""
        return len(self.value)

    def __getitem__(self, key: Any) -> Any:
        """Index access to the value."""
        return self.value[key]

    def __contains__(self, item: Any) -> bool:
        """Check if item is in the value."""
        return item in self.value

    def __str__(self) -> str:
        """String representation of the value."""
        return str(self.value)

    def __format__(self, format_spec: str) -> str:
        """Return a FormattedVar that reacts to changes."""
        return FormattedVar(format(self.value, format_spec), self, format_spec)

    def __int__(self) -> int:
        """Integer conversion."""
        return int(self.value)

    def __float__(self) -> float:
        """Float conversion."""
        return float(self.value)

    def __repr__(self) -> str:
        """Detailed representation of the variable."""
        return f"Var({repr(self.value)})"

    def __call__(self, *args, as_component=None, **kwargs) -> "Component":
        """Create a two-way binding component for this variable."""
        from ..components.two_way import TwoWayBindingElement
        if self._component_factory is not None:
            return self._component_factory(bind_var=self, *args, **kwargs)
        if as_component is not None:
            if isinstance(as_component, str):
                comp_cls = ctx.TWO_WAY_REGISTRY[as_component]
            elif issubclass(as_component, TwoWayBindingElement):
                comp_cls = as_component
            else:
                raise TypeError("as_component must be a string alias or TwoWayBindingElement subclass")
        else:
            if ctx.default_two_way_class is None:
                raise RuntimeError("No default two-way component registered.")
            comp_cls = ctx.default_two_way_class
        return comp_cls(bind_var=self, *args, **kwargs)

    def bind_with(self, component_factory: Callable[..., "Component"]) -> "Var":
        """Bind this variable to a component factory for two-way binding."""
        self._component_factory = component_factory
        return self

    def _notify(self, session: "Session") -> None:
        """Notify all observers of a change."""
        for observer, callbacks in list(self._observers.items()):
            for cb in callbacks:
                cb(observer, self, session)
        for cb in self._raw_callbacks:
            cb(self, session)

    def observe(self, comp: "Component", cb: Callable) -> None:
        """Register an observer component and callback."""
        if comp not in self._observers:
            self._observers[comp] = []
        self._observers[comp].append(cb)

    def _add_raw_callback(self, cb: Callable) -> Callable[[], None]:
        """Add a raw callback that receives (var, session) on changes."""
        self._raw_callbacks.append(cb)
        def unsubscribe():
            if cb in self._raw_callbacks:
                self._raw_callbacks.remove(cb)
        return unsubscribe


def var(initial_value: Any = "", *, name: Optional[str] = None) -> Var:
    """Create a reactive variable with an optional stable name."""
    v = Var(initial_value)
    if name is not None:
        v._set_stable_key(name)
    return v


def auto_name_vars(module: Any) -> None:
    """Automatically assign stable names to all Var instances in a module."""
    for var_name, obj in module.__dict__.items():
        if isinstance(obj, Var) and not obj._auto_named:
            obj._set_stable_key(var_name)
