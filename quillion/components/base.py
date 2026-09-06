"""
Component: base class for all UI elements.
UIComponentMeta wires up event handlers and assigns stable IDs.
"""

from __future__ import annotations

import asyncio
import inspect
import re
import uuid
from collections.abc import Callable
from typing import Any

from .. import _context as ctx


def snake_to_camel(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_css_property_name(key: str) -> str:
    """
    Convert various naming conventions to kebab-case CSS property.
    Handles: camelCase, snake_case, and direct CSS properties.
    """
    # If it's already snake_case, convert to camelCase first
    if "_" in key:
        key = snake_to_camel(key)

    kebab = re.sub(r"([A-Z])", r"-\1", key).lower()
    return kebab


class UIComponentMeta(type):
    """Metaclass that post-processes Component instances on creation."""

    def __call__(cls, *args, **kwargs):
        style: dict[str, Any] = {}
        class_name: str | None = kwargs.pop("class_name", None) or kwargs.pop(
            "className", None
        )
        other: dict[str, Any] = {}

        reserved = {
            "children",
            "bind_var",
            "on_click",
            "level",
            "placeholder",
            "type",
            "path",
            "label",
            "class_name",
            "className",
            "src",
            "alt",
            "href",
            "rel",
        }
        for key, value in kwargs.items():
            if key not in reserved and not key.startswith("on_"):
                style[key] = value
            else:
                other[key] = value

        inst = super().__call__(*args, **other)
        inst._id = str(uuid.uuid4())[:8]
        inst._event_handlers = {}
        inst._style = style
        inst._class_name = class_name

        for attr in dir(inst):
            if attr.startswith("on_") and callable(getattr(inst, attr)):
                original = getattr(inst, attr)
                event_name = attr[3:]
                inst._event_handlers[event_name] = original

                def _wrap(orig: Callable, _evt: str):
                    def wrapper(event_data: dict | None = None):
                        if inspect.signature(orig).parameters:
                            result = orig(event_data)
                        else:
                            result = orig()
                        session = ctx.current_session.get()
                        if session and ctx.quillion_app:
                            asyncio.create_task(
                                ctx.quillion_app._delayed_process(session)
                            )
                        return result

                    return wrapper

                setattr(inst, attr, _wrap(original, event_name))

        if hasattr(inst, "_post_init"):
            inst._post_init()
        return inst


class Component(metaclass=UIComponentMeta):
    tag_name: str = "div"

    _id: str
    _event_handlers: dict[str, Callable]
    _style: dict[str, Any]
    _class_name: str | None

    def __init__(self, **kwargs):
        self._id = ""
        self._event_handlers = {}
        self._style = {}
        self._class_name = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_props(self) -> dict[str, Any]:
        props: dict[str, Any] = {}
        if self._style:
            css_items = []
            for k, v in self._style.items():
                css_prop = to_css_property_name(k)
                css_items.append(f"{css_prop}: {v}")
            props["style"] = "; ".join(css_items)
        if self._class_name:
            props["className"] = self._class_name
        return props

    def get_children(self) -> list[Component]:
        return getattr(self, "children", [])
