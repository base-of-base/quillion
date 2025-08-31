from typing import Optional, Dict, List, Any, Callable
import uuid


class Element:
    def __init__(
        self,
        tag: str,
        text: Optional[str] = None,
        on_click: Optional[Callable] = None,
        inline_style_properties: Optional[Dict[str, str]] = None,
        classes: Optional[List[str]] = None,
        key: Optional[str] = None,
    ):
        self.tag = tag
        self.text = text
        self.on_click = on_click
        self.children: List["Element"] = []
        self.attributes = {}
        self.inline_style_properties = inline_style_properties or {}
        self.css_classes = classes or []
        self.key = key

    def append(self, *children: "Element"):
        for child in children:
            self.children.append(child)
        return self

    def add_class(self, class_name: str):
        if class_name not in self.css_classes:
            self.css_classes.append(class_name)

    def _convert_inline_style_to_css_string(self) -> str:
        css_parts = []
        for k, v in self.inline_style_properties.items():
            css_key = k.replace("_", "-")
            css_parts.append(f"{css_key}: {v};")
        return " ".join(css_parts)

    def to_dict(self, app) -> Dict[str, Any]:
        from ..components import Component

        data = {"tag": self.tag, "attributes": {}, "text": self.text, "children": []}
        if self.on_click:
            cb_id = str(uuid.uuid4())
            app.callbacks[cb_id] = self.on_click
            data["attributes"]["data-callback-id"] = cb_id
        if self.inline_style_properties:
            data["attributes"]["style"] = self._convert_inline_style_to_css_string()
        if self.css_classes:
            data["attributes"]["class"] = " ".join(self.css_classes)
        if self.key:
            data["key"] = self.key
        for child in self.children:
            if isinstance(child, Component) and child.key:
                if app._current_rendering_page:
                    resolved_child_instance = (
                        app._current_rendering_page._get_or_create_component_instance(
                            child
                        )
                    )
                    data["children"].append(resolved_child_instance.to_dict(app))
                else:
                    data["children"].append(child.to_dict(app))
            else:
                data["children"].append(child.to_dict(app))
        return data
