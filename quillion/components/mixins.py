"""
Reusable mixins for components.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from .base import Component

if TYPE_CHECKING:
    from ..session import Session
    from ..var import Var

from .. import _context as ctx


class TextMixin:
    """Renders mixed text + Var parts; re-renders when any Var changes."""

    _parts: tuple[Any, ...]
    _vars: list[Var]
    content: str

    def __init__(self, *parts: Any, **kwargs: Any) -> None:
        self._parts = parts
        self._vars = [p for p in parts if hasattr(p, "observe")]
        self.content = "".join(str(p) for p in parts)
        super().__init__(**kwargs)

    def _post_init(self) -> None:
        for v in self._vars:
            v.observe(cast("Component", self), lambda c, v, s: self._update(s))

    def _update(self, session: Session | None) -> None:
        self.content = "".join(str(p) for p in self._parts)
        if session is None:
            session = ctx.current_session.get()
        if session:
            session.updater.schedule_update(cast("Component", self))

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {"textContent": self.content}
        props.update(cast("Component", super()).get_props())
        return props


class ReactiveContainerMixin:
    """
    Mixin for containers (Div, Span etc).
    Becomes reactive automatically if `Var` children detected
    """

    _children_spec: tuple[Any, ...]
    _vars: list[Var]
    _children_cache: list[Component]
    _is_reactive: bool

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        self._children_spec = children
        self._vars = self._extract_vars(children)
        self._is_reactive = bool(self._vars)
        self._children_cache = self._build_children(children)
        super().__init__(**kwargs)
        self.children: list[Component] = self._children_cache

    def _extract_vars(self, items: Any) -> list[Var]:
        """Extracts Var from struct."""
        result: list[Var] = []
        if hasattr(items, "observe") and (hasattr(items, "_key") or hasattr(items, "_dependencies")):
            result.append(items)
        elif isinstance(items, (list, tuple)):
            for item in items:
                result.extend(self._extract_vars(item))
        return result

    def _build_children(self, items: Any) -> list[Component]:
        """Converts children to components."""
        from .elements import Text

        result: list[Component] = []

        if hasattr(items, "observe") and (hasattr(items, "_key") or hasattr(items, "_dependencies")):
            value: Any = items.value if hasattr(items, "value") else items
            if isinstance(value, (list, tuple)):
                for item in value:
                    result.extend(self._build_children(item))
            elif isinstance(value, Component):
                result.append(value)
            else:
                result.append(Text(str(value)))

        elif isinstance(items, (list, tuple)):
            for item in items:
                result.extend(self._build_children(item))

        elif isinstance(items, Component):
            result.append(items)

        else:
            result.append(Text(str(items)) if not isinstance(items, str) else Text(items))

        return result

    def _post_init(self) -> None:
        """Subscribes to every `Var`."""
        if self._vars:
            for v in self._vars:
                v.observe(cast("Component", self), lambda c, v, s: self._update_children(s))

    def _update_children(self, session: Session | None) -> None:
        """Rebuild children on `Var` changes."""
        self._children_cache = self._build_children(self._children_spec)
        self.children = self._children_cache
        if session is None:
            session = ctx.current_session.get()
        if session:
            session.updater.schedule_update(cast("Component", self))

    def get_children(self) -> list[Component]:
        return self._children_cache
