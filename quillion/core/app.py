import inspect
import json
import websockets
import re
from typing import Dict, Optional

from quillion.utils.finder import RouteFinder
from .crypto import Crypto
from .messaging import Messaging
from .server import ServerConnection
from .router import Path
from ..pages.base import Page, PageMeta
from ..components import State
from ..utils.regex_parser import RegexParser, RouteType


class Quillion:
    _instance = None

    def __init__(self):
        Quillion._instance = self
        self.callbacks: Dict[str, callable] = {}
        self.current_page: Optional[Page] = None
        self.current_path: Optional[str] = None
        self.websocket = None
        self._state_instances: Dict[type, "State"] = {}
        self.style_tag_id = "quillion-dynamic-styles"
        self._current_rendering_page: Optional[Page] = None
        self.crypto = Crypto()
        self.messaging = Messaging(self)
        self.server_connection = ServerConnection()
        Path.init(self)

    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        self.websocket = websocket
        self._state_instances = {}
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
                    raise
        except Exception as e:
            print(f"[{websocket.id}] Error: {e}")
            raise
        finally:
            self._state_instances.clear()
            self.crypto.cleanup(websocket)

    async def navigate(self, path: str, websocket=None):
        page_cls, params, _ = RouteFinder.find_route(path)

        if page_cls and websocket:
            if not self.current_page or self.current_page.__class__ != page_cls:
                self.current_page = page_cls(params=params or {})
            self.current_path = path
            await self.render_current_page(websocket)
        else:
            print(f"[{websocket.id}] Received unknow path: {path}")

    def redirect(self, path: str):
        if self.websocket:
            import asyncio

            asyncio.create_task(self.navigate(path, self.websocket))

    async def render_current_page(self, websocket: websockets.WebSocketServerProtocol):
        if not self.current_page or not websocket:
            return

        self._current_rendering_page = self.current_page
        self.current_page._rendered_component_keys.clear()

        for component_instance in self.current_page._component_instance_cache.values():
            component_instance._reset_hooks()

        try:
            root_element = self.current_page.render(**self.current_page.params)

            # async funcs support. looks like cringe but it works
            if inspect.isawaitable(root_element):
                root_element = await root_element

            from ..components.ui.container import Container

            if not isinstance(root_element, Container):
                root_element = Container(root_element)

            page_class_name = self.current_page.get_page_class_name()
            root_element.add_class(page_class_name)
            tree = root_element.to_dict(self)
            self.current_page._cleanup_old_component_instances()
            content_message_for_encryption = {
                "action": "render_page",
                "path": self.current_path,
                "content": [tree],
            }

            message_to_client = self.crypto.encrypt_response(
                websocket, content_message_for_encryption
            )

            await websocket.send(json.dumps(message_to_client))
        finally:
            self._current_rendering_page = None

    def start(self, host="0.0.0.0", port=1337):
        self.server_connection.start(self.handler, host, port)
