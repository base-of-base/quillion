"""
Reusable mixins for components.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING, cast

if TYPE_CHECKING:
    from ..var import Var
    from ..session import Session
    from .base import Component


class TextMixin:
    """Renders mixed text + Var parts; re-renders when any Var changes."""

    _parts: Tuple[Any, ...]
    _vars: List["Var"]
    content: str

    def __init__(self, *parts: Any, **kwargs: Any) -> None:
        self._parts  = parts
        self._vars   = [p for p in parts if hasattr(p, "observe")]
        self.content = "".join(str(p) for p in parts)
        super().__init__(**kwargs)

    def _post_init(self) -> None:
        for v in self._vars:
            v.observe(cast("Component", self), lambda c, v, s: self._update(s))

    def _update(self, session: Optional["Session"]) -> None:
        self.content = "".join(str(p) for p in self._parts)
        if session:
            session.updater.schedule_update(cast("Component", self))

    def get_props(self) -> Dict[str, Any]:
        props = {"textContent": self.content}
        props.update(cast("Component", super(TextMixin, self)).get_props())
        return props
