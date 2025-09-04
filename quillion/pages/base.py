import asyncio
import uuid
import re
from typing import Dict, Optional, Tuple
from ..components.base import Component
from ..ui.element import Element

class PageMeta(type):
    _registry: Dict[str, "Page"] = {}
    _dynamic_routes: Dict[str, Tuple[re.Pattern, "Page"]] = {}

    def __init__(cls, name, bases, attrs):
        if hasattr(cls, "router") and cls.router:
            if "{" in cls.router and "}" in cls.router:
                pattern = re.escape(cls.router)
                pattern = pattern.replace(r"\{", r"(?P<").replace(r"\}", r">[^\\/]+)")
                cls._regex = re.compile(f"^{pattern}$")
                PageMeta._dynamic_routes[cls.router] = (cls._regex, cls)
            else:
                PageMeta._registry[cls.router] = cls
        super().__init__(name, bases, attrs)

class Page(metaclass=PageMeta):
    router: str = None
    _page_class_name: Optional[str] = None

    def __init__(self, params: Optional[Dict[str, str]] = None):
        self._component_instance_cache: Dict[str, Component] = {}
        self._rendered_component_keys: set[str] = set()
        self.params = params or {}

    def render(self, **params) -> Element:
        raise NotImplementedError

    def get_page_class_name(self) -> str:
        if self._page_class_name is None:
            clean_router = self.router.strip("/").replace("/", "-")
            if not clean_router:
                clean_router = "home"
            self._page_class_name = (
                f"quillion-page-{clean_router}-{uuid.uuid4().hex[:6]}"
            )
        return self._page_class_name

    def _get_or_create_component_instance(
        self, new_component_declaration: Component
    ) -> Component:
        from ..core.app import Quillion

        key = new_component_declaration.key
        if not key:
            return new_component_declaration
        if key not in self._component_instance_cache:
            self._component_instance_cache[key] = new_component_declaration

            async def rerender_callback():
                app = Quillion._instance
                if app and app.websocket:
                    await app.render_current_page(app.websocket)

            new_component_declaration._rerender_callback = rerender_callback
        else:
            cached_instance = self._component_instance_cache[key]
            cached_instance.text = new_component_declaration.text
            cached_instance.on_click = new_component_declaration.on_click
            cached_instance.inline_style_properties.update(
                new_component_declaration.inline_style_properties
            )
            for cls in new_component_declaration.css_classes:
                if cls not in cached_instance.css_classes:
                    cached_instance.css_classes.append(cls)
            if not cached_instance._rerender_callback:

                async def rerender_callback():
                    app = Quillion._instance
                    if app and app.websocket:
                        await app.render_current_page(app.websocket)

                cached_instance._rerender_callback = rerender_callback
            new_component_declaration = cached_instance
        self._rendered_component_keys.add(key)
        return new_component_declaration

    def _cleanup_old_component_instances(self):
        keys_to_remove = [
            k
            for k in self._component_instance_cache
            if k not in self._rendered_component_keys
        ]
        for key in keys_to_remove:
            self._component_instance_cache[key]._rerender_callback = None
            del self._component_instance_cache[key]
        self._rendered_component_keys.clear()