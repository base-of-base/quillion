from typing import Any, List
from .element import Element


class Container(Element):
    def __init__(self, *children_or_style_properties: Any, **kwargs):
        from ..components import Component
        from ..styles import StyleProperty

        super().__init__("div", **kwargs)
        self.children: List[Element] = []
        self.style_properties: List["StyleProperty"] = []
        for item in children_or_style_properties:
            if isinstance(item, (Element, Component)):
                self.children.append(item)
            elif isinstance(item, StyleProperty):
                self.style_properties.append(item)
            else:
                print(f"Warning: Unexpected item type in Container: {type(item)}")
