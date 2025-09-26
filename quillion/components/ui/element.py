from typing import Optional, Dict, List, Any, Callable
import uuid
import re


class StyleProperty:
    def __init__(self, key: str, value):
        self._key = key
        self._value = value

    def to_css_properties_dict(self) -> Dict[str, str]:
        css_key = re.sub(r"([A-Z])", r"-\1", self._key).lower().replace("_", "-")
        css_value = str(self._value)
        return {css_key: css_value}


class Element:
    def __init__(
        self,
        tag: str,
        text: Optional[str] = None,
        event_handlers: Optional[Dict[str, Callable]] = None,
        inline_style_properties: Optional[Dict[str, str]] = None,
        classes: Optional[List[str]] = None,
        key: Optional[str] = None,
        class_name: Optional[str] = None,
        **kwargs: Any,
    ):
        self.tag = tag
        self.text = text
        self.event_handlers = event_handlers or {}
        self.children: List["Element"] = []
        self.attributes = {}
        self.inline_style_properties = inline_style_properties or {}
        self.css_classes = classes or []
        self.key = key
        self.style_properties: List["StyleProperty"] = []

        if class_name:
            self.css_classes.append(class_name)

        for prop_key, prop_value in kwargs.items():
            if prop_key.startswith("on_") and callable(prop_value):
                event_name = prop_key[3:]  # "on_" is exile
                self.event_handlers[event_name] = prop_value
            else:
                self.attributes[prop_key] = prop_value

    def append(self, *children: "Element"):
        for child in children:
            self.children.append(child)
        return self

    def add_class(self, class_name: str):
        if class_name not in self.css_classes:
            self.css_classes.append(class_name)

    def add_event_handler(self, event_name: str, handler: Callable):
        self.event_handlers[event_name] = handler

    def set_attribute(self, name: str, value: Any):
        self.attributes[name] = value

    def to_dict(self, app) -> Dict[str, Any]:
        from ...components import CSS

        if isinstance(self, CSS):
            return self.to_dict(app)

        data = {
            "tag": self.tag,
            "attributes": self.attributes.copy(),
            "text": self.text,
            "children": [],
        }

        for event_name, handler in self.event_handlers.items():
            cb_id = str(uuid.uuid4())
            app.callbacks[cb_id] = handler
            data["attributes"][f"on{event_name}"] = cb_id

        if self.inline_style_properties or self.style_properties:
            style_dict = {}
            style_dict.update(self.inline_style_properties)
            for prop in self.style_properties:
                style_dict.update(prop.to_css_properties_dict())
            css_parts = [f"{k.replace('_', '-')}: {v};" for k, v in style_dict.items()]
            data["attributes"]["style"] = " ".join(css_parts)

        if self.css_classes:
            if "class" in data["attributes"]:
                existing_class = data["attributes"]["class"]
                data["attributes"][
                    "class"
                ] = f"{existing_class} {' '.join(self.css_classes)}"
            else:
                data["attributes"]["class"] = " ".join(self.css_classes)

        if self.key:
            data["key"] = self.key

        for child in self.children:
            if isinstance(child, CSS):
                data["children"].append(child.to_dict(app))
            elif hasattr(child, "to_dict"):
                data["children"].append(child.to_dict(app))
            else:
                data["children"].append(child)

        return data
