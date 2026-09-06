"""
Reusable mixins for components.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, cast
from .base import Component
if TYPE_CHECKING:
    from ..var import Var
    from ..session import Session

from .. import _context as ctx


class TextMixin:
    """Renders mixed text + Var parts; re-renders when any Var changes."""

    _parts: Tuple[Any, ...]
    _vars: List["Var"]
    content: str

    def __init__(self, *parts: Any, **kwargs: Any) -> None:
        self._parts = parts
        self._vars = [p for p in parts if hasattr(p, "observe")]
        self.content = "".join(str(p) for p in parts)
        super().__init__(**kwargs)

    def _post_init(self) -> None:
        for v in self._vars:
            v.observe(cast("Component", self), lambda c, v, s: self._update(s))

    def _update(self, session: Optional["Session"]) -> None:
        self.content = "".join(str(p) for p in self._parts)
        if session is None:
            session = ctx.current_session.get()
        if session:
            session.updater.schedule_update(cast("Component", self))

    def get_props(self) -> Dict[str, Any]:
        props = {"textContent": self.content}
        props.update(cast("Component", super(TextMixin, self)).get_props())
        return props


class ReactiveContainerMixin:
    """
    Mixin for containers (Div, Span etc).
    Becomes reactive automatically if `Var` children detected
    """
    
    _children_spec: Tuple[Any, ...]
    _vars: List["Var"]
    _children_cache: List["Component"]
    _is_reactive: bool

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        self._children_spec = children
        self._vars = self._extract_vars(children)
        self._is_reactive = bool(self._vars)
        self._children_cache = self._build_children(children)
        super().__init__(**kwargs)
        self.children = self._children_cache

    def _extract_vars(self, items: Any) -> List["Var"]:
        """Extracts Var from struct."""
        result = []
        if hasattr(items, "observe") and (hasattr(items, "_key") or hasattr(items, "_dependencies")):
            result.append(items)
        elif isinstance(items, (list, tuple)):
            for item in items:
                result.extend(self._extract_vars(item))
        return result

    def _build_children(self, items: Any) -> List["Component"]:
        """Converts children to components."""
        from .elements import Text
        
        result = []
        
        # Var or ComputedValue
        if hasattr(items, "observe") and (hasattr(items, "_key") or hasattr(items, "_dependencies")):
            value = items.value if hasattr(items, "value") else items
            if isinstance(value, (list, tuple)):
                for item in value:
                    result.extend(self._build_children(item))
            elif isinstance(value, Component):
                result.append(value)
            else:
                result.append(Text(str(value)))
        
        # List or tuple - process each element
        elif isinstance(items, (list, tuple)):
            for item in items:
                result.extend(self._build_children(item))
        
        # Ready component
        elif isinstance(items, Component):
            result.append(items)
        
        # Primitive
        else:
            result.append(Text(str(items)) if not isinstance(items, str) else Text(items))
        
        return result

    def _post_init(self) -> None:
        """Subscribes to every `Var`."""
        if self._vars:
            for v in self._vars:
                v.observe(cast("Component", self), lambda c, v, s: self._update_children(s))

    def _update_children(self, session: Optional["Session"]) -> None:
        """Rebuild children on `Var` changes."""
        self._children_cache = self._build_children(self._children_spec)
        self.children = self._children_cache
        if session is None:
            session = ctx.current_session.get()
        if session:
            session.updater.schedule_update(cast("Component", self))

    def get_children(self) -> List["Component"]:
        return self._children_cache