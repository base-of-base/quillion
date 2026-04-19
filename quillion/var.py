"""
Reactive variable (Var) and related utilities.
"""

from __future__ import annotations
import uuid
from typing import TYPE_CHECKING, Any, Callable, Optional
from weakref import WeakKeyDictionary

if TYPE_CHECKING:
    from .components.base import Component

from . import _context as ctx


class Var:
    """A reactive variable whose value is stored per-session."""

    _key: str
    _initial: Any
    _observers: WeakKeyDictionary
    _component_factory: Optional[Callable[..., "Component"]]
    _auto_named: bool

    def __init__(self, initial_value: Any = "") -> None:
        self._key = str(uuid.uuid4())
        self._initial = initial_value
        self._observers = WeakKeyDictionary()
        self._component_factory = None
        self._auto_named = False

    def _set_stable_key(self, name: str) -> None:
        if name in ctx.VAR_NAME_REGISTRY:
            self._key = ctx.VAR_NAME_REGISTRY[name]
        else:
            ctx.VAR_NAME_REGISTRY[name] = self._key
        self._auto_named = True

    @property
    def value(self) -> Any:
        session = ctx.current_session.get()
        if session is None:
            return self._initial
        return session.state.get_var_value(self._key, self._initial)

    @value.setter
    def value(self, new_value: Any) -> None:
        session = ctx.current_session.get()
        if session is None:
            raise RuntimeError("Var.value can only be set inside a session")
        session.state.set_var_value(self._key, new_value)
        self._notify(session)

    def __add__(self, other: Any) -> "Var":
        self.value += other
        return self

    def __sub__(self, other: Any) -> "Var":
        self.value -= other
        return self

    def __format__(self, format_spec: str) -> str:
        return format(self.value, format_spec)

    def __str__(self) -> str:
        return str(self.value)


    def __call__(self, *args, as_component=None, **kwargs) -> "Component":
        from .components.two_way import TwoWayBindingElement

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
        self._component_factory = component_factory
        return self

    def _notify(self, session) -> None:
        for comp, cb in list(self._observers.items()):
            cb(comp, self, session)

    def observe(self, comp, cb: Callable) -> None:
        self._observers[comp] = cb


def var(initial_value: Any = "", *, name: Optional[str] = None) -> Var:
    """Create a reactive Var, optionally with a stable name."""
    v = Var(initial_value)
    if name is not None:
        v._set_stable_key(name)
    return v


def auto_name_vars(module: Any) -> None:
    """Assign stable keys to all module-level Vars (called after (re)loading)."""
    for var_name, obj in module.__dict__.items():
        if isinstance(obj, Var) and not obj._auto_named:
            obj._set_stable_key(var_name)
