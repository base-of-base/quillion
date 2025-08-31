import json
import websockets
from typing import Dict, Optional
from .router import Path
from .crypto import Crypto
from .messaging import Messaging
from .server import ServerConnection
from ..pages.base import Page, PageMeta
from ..ui.element import Element


class Quillion:
    def __init__(self):
        self.callbacks: Dict[str, callable] = {}
        self.current_page: Optional[Page] = None
        self.websocket = None
        Path.init(self)
        self.style_tag_id = "quillion-dynamic-styles"
        self._current_rendering_page: Optional[Page] = None
        self.crypto = Crypto()
        self.messaging = Messaging(self)
        self.server_connection = ServerConnection()

    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        self.websocket = websocket
        initial_path = websocket.path
        try:
            public_key_message = await websocket.recv()
            data = json.loads(public_key_message)
            if await self.crypto.handle_key_exchange(websocket, data):
                await self.navigate(initial_path, websocket)
            else:
                return
            async for message in websocket:
                try:
                    data = json.loads(message)
                    inner_data = await self.crypto.decrypt_message(websocket, data)
                    if inner_data:
                        await self.messaging.process_inner_message(
                            websocket, inner_data
                        )
                except json.JSONDecodeError as e:
                    print(
                        f"[{websocket.id}] json decode error: {e} - msg: {message}. not decrypted?"
                    )
                except Exception as e:
                    print(f"[{websocket.id}] Error: {e}")
        except Exception as e:
            print(f"[{websocket.id}] Error: {e}")
        finally:
            self.crypto.cleanup(websocket)

    async def navigate(self, path: str, websocket: websockets.WebSocketServerProtocol):
        page_cls = PageMeta._registry.get(path)
        if page_cls:
            if not self.current_page or self.current_page.__class__ != page_cls:
                self.current_page = page_cls()
            await self.render_current_page(websocket)

    def _collect_css_rules(self) -> Dict[str, Dict[str, str]]:
        from ..styles.base import StyleMeta
        from ..styles.properties import (
            ParagraphBase,
            ButtonBase,
            ButtonHover,
            LinkBase,
            LinkHover,
            FontFamily,
            Background,
            Margin,
            Padding,
            MinHeight,
            DisplayFlex,
        )
        from ..ui.container import Container

        all_css_rules: Dict[str, Dict[str, str]] = {}
        for global_style_instance in StyleMeta._global_styles_registry:
            global_style_container = global_style_instance.styles()
            if isinstance(global_style_container, Container):
                for prop_obj in global_style_container.style_properties:
                    if isinstance(prop_obj, ParagraphBase):
                        if "p" not in all_css_rules:
                            all_css_rules["p"] = {}
                        all_css_rules["p"].update(prop_obj.to_css_properties_dict())
                    elif isinstance(prop_obj, ButtonBase):
                        if "button" not in all_css_rules:
                            all_css_rules["button"] = {}
                        all_css_rules["button"].update(
                            prop_obj.to_css_properties_dict()
                        )
                    elif isinstance(prop_obj, ButtonHover):
                        if "button:hover" not in all_css_rules:
                            all_css_rules["button:hover"] = {}
                        all_css_rules["button:hover"].update(
                            prop_obj.to_css_properties_dict()
                        )
                    elif isinstance(prop_obj, LinkBase):
                        if "a" not in all_css_rules:
                            all_css_rules["a"] = {}
                        all_css_rules["a"].update(prop_obj.to_css_properties_dict())
                    elif isinstance(prop_obj, LinkHover):
                        if "a:hover" not in all_css_rules:
                            all_css_rules["a:hover"] = {}
                        all_css_rules["a:hover"].update(
                            prop_obj.to_css_properties_dict()
                        )
                    elif isinstance(
                        prop_obj,
                        (
                            FontFamily,
                            Background,
                            Margin,
                            Padding,
                            MinHeight,
                            DisplayFlex,
                        ),
                    ):
                        if "body" not in all_css_rules:
                            all_css_rules["body"] = {}
                        all_css_rules["body"].update(prop_obj.to_css_properties_dict())
                    else:
                        pass
            else:
                print(
                    f"Warning: Global style {global_style_instance.__class__.__name__}.styles() did not return a Container."
                )
        if (
            self.current_page
            and hasattr(self.current_page, "styles")
            and callable(getattr(self.current_page, "styles"))
        ):
            from ..utils.decorators import style
            from ..styles import Style

            styles_method = getattr(self.current_page, "styles")
            if hasattr(styles_method, "_is_style") and styles_method._is_style:
                page_style_instance = styles_method()
                if isinstance(page_style_instance, Style):
                    page_style_container = page_style_instance.styles()
                    if isinstance(page_style_container, Container):
                        page_class_name = self.current_page.get_page_class_name()
                        page_root_selector = f".{page_class_name}"
                        if page_root_selector not in all_css_rules:
                            all_css_rules[page_root_selector] = {}
                        for prop_obj in page_style_container.style_properties:
                            if isinstance(prop_obj, ParagraphBase):
                                if f"{page_root_selector} p" not in all_css_rules:
                                    all_css_rules[f"{page_root_selector} p"] = {}
                                all_css_rules[f"{page_root_selector} p"].update(
                                    prop_obj.to_css_properties_dict()
                                )
                            elif isinstance(prop_obj, ButtonBase):
                                if f"{page_root_selector} button" not in all_css_rules:
                                    all_css_rules[f"{page_root_selector} button"] = {}
                                all_css_rules[f"{page_root_selector} button"].update(
                                    prop_obj.to_css_properties_dict()
                                )
                            elif isinstance(prop_obj, ButtonHover):
                                if (
                                    f"{page_root_selector} button:hover"
                                    not in all_css_rules
                                ):
                                    all_css_rules[
                                        f"{page_root_selector} button:hover"
                                    ] = {}
                                all_css_rules[
                                    f"{page_root_selector} button:hover"
                                ].update(prop_obj.to_css_properties_dict())
                            elif isinstance(prop_obj, Container):
                                for nested_prop in prop_obj.style_properties:
                                    if isinstance(nested_prop, StyleProperty):
                                        all_css_rules[page_root_selector].update(
                                            nested_prop.to_css_properties_dict()
                                        )
                            else:
                                all_css_rules[page_root_selector].update(
                                    prop_obj.to_css_properties_dict()
                                )
                    else:
                        print(
                            f"Warning: Page style {self.current_page.__class__.__name__}.styles().styles() did not return a Container."
                        )
                else:
                    print(
                        f"Warning: Page {self.current_page.__class__.__name__}.styles() did not return a Style instance."
                    )
        return all_css_rules

    async def render_current_page(self, websocket: websockets.WebSocketServerProtocol):
        if not self.current_page or not websocket:
            return
        self._current_rendering_page = self.current_page
        self.current_page._rendered_component_keys.clear()
        for component_instance in self.current_page._component_instance_cache.values():
            component_instance._reset_hooks()
        try:
            css_rules = self._collect_css_rules()
            root_element = self.current_page.render()
            page_class_name = self.current_page.get_page_class_name()
            root_element.add_class(page_class_name)
            tree = root_element.to_dict(self)
            self.current_page._cleanup_old_component_instances()
            content_message_for_encryption = {
                "action": "render_page",
                "path": self.current_page.router,
                "content": [tree],
                "css_rules": css_rules,
            }
            message_to_client = self.crypto.encrypt_response(
                websocket, content_message_for_encryption
            )
            await websocket.send(json.dumps(message_to_client))
        finally:
            self._current_rendering_page = None

    def start(self, host="0.0.0.0", port=1337):
        self.server_connection.start(self.handler, host, port)
