"""
InputComponent: <input> element with two-way Var binding.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from ..var import Var
from .two_way import TwoWayBindingElement


class InputComponent(TwoWayBindingElement):
    tag_name = "input"
    _component_alias = "input"
    _is_default = True

    def __init__(
        self,
        bind_var: Optional[Var] = None,
        placeholder: str = "",
        type: str = "text",
        **kwargs: Any,
    ) -> None:
        super().__init__(bind_var=bind_var, **kwargs)
        self.placeholder = placeholder
        self.type        = type

    def get_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {"value": self.get_current_value(), "type": self.type}
        if self.placeholder:
            props["placeholder"] = self.placeholder
        props.update(super().get_props())
        return props

    def on_input(self, event_data: Optional[Dict] = None) -> None:
        if event_data and "value" in event_data:
            self.update_var_from_event(event_data["value"])
