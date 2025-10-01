import os
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
                event_name = prop_key[3:]
                self.event_handlers[event_name] = prop_value
            elif prop_key == "style":
                if isinstance(prop_value, str):
                    styles = prop_value.split(";")
                    for style in styles:
                        if ":" in style:
                            css_key, css_value = style.split(":", 1)
                            self.inline_style_properties[css_key.strip()] = (
                                css_value.strip()
                            )
            else:
                self.style_properties.append(StyleProperty(prop_key, prop_value))

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

        all_styles = {}

        all_styles.update(self.inline_style_properties)

        for prop in self.style_properties:
            all_styles.update(prop.to_css_properties_dict())

        if all_styles:
            css_parts = [f"{k}: {v};" for k, v in all_styles.items()]
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


class MediaElement(Element):
    def __init__(
        self,
        tag: str,
        src: Optional[str] = None,
        event_handlers: Optional[Dict[str, Callable]] = None,
        inline_style_properties: Optional[Dict[str, str]] = None,
        classes: Optional[List[str]] = None,
        key: Optional[str] = None,
        class_name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            tag,
            src,
            event_handlers,
            inline_style_properties,
            classes,
            key,
            class_name,
            **kwargs,
        )
        self.src = src

    def to_dict(self, app) -> Dict[str, Any]:
        result = super().to_dict(app)
        if self.src:
            if self.src.startswith("http://") or self.src.startswith("https://"):
                result["attributes"]["src"] = self.src
            else:
                result["attributes"][
                    "src"
                ] = f"{app.asset_server_url}/{self.src.replace(f'{app.assets_path}/', '')}"
        return result
