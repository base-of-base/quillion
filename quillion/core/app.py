import inspect
import json
import websockets
import os
from typing import Dict, Optional, List

from quillion.utils.finder import RouteFinder
from .crypto import Crypto
from .messaging import Messaging
from .server import AssetServer, ServerConnection
from .router import Path
from ..pages.base import Page
from ..components import State


class Quillion:
    _instance = None

    def __init__(self):
        Quillion._instance = self
        self.callbacks: Dict[str, сallable] = {}
        self.current_page: Optional[Page] = None
        self.current_path: Optional[str] = None
        assets_host = os.environ.get("QUILLION_ASSET_HOST", "localhost")
        assets_port = os.environ.get("QUILLION_ASSET_PORT", "1338")
        self.assets_path = os.environ.get("QUILLION_ASSET_PATH", "")
        self.asset_server_url = f"http://{assets_host}:{assets_port}".rstrip("/")
        self.asset_server = AssetServer(assets_dir=self.assets_path)
        self.websocket = None
        self._state_instances: Dict[type, "State"] = {}
        self.style_tag_id = "quillion-dynamic-styles"
        self._current_rendering_page: Optional[Page] = None
        self.crypto = Crypto()
        self.messaging = Messaging(self)
        self.server_connection = ServerConnection()
        Path.init(self)
        self.external_css_files: List[str] = []
        self._css_cache: Dict[str, str] = {}

    def _load_css_file(self, css_file: str) -> str:
        from quillion_cli.debug.debugger import debugger

        if css_file in self._css_cache:
            return self._css_cache[css_file]

        with open(css_file, "r", encoding="utf-8") as f:
            content = f.read()
            self._css_cache[css_file] = content
            debugger.info(f"Loaded styles -> {css_file}")
            return content

    async def handler(self, websocket: websockets.WebSocketServerProtocol):
        from quillion_cli.debug.debugger import debugger

        self.websocket = websocket
        if self:
            connection_id = (
                f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            )
            debugger.info(f"[{connection_id}] Received new connection")
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
                    connection_id = (
                        f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
                    )
                    print(
                        f"[{connection_id}] json decode error: {e} - msg: {message}. not decrypted?"
                    )
                except Exception as e:
                    connection_id = (
                        f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
                    )
                    debugger.error(f"[{connection_id}] Error: {e}")
                    raise
        except Exception as e:
            connection_id = (
                f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            )
            debugger.error(f"[{connection_id}] Error: {e}")
            raise
        finally:
            self._state_instances.clear()
            self.crypto.cleanup(websocket)

    async def navigate(
        self, path: str, websocket: websockets.WebSocketServerProtocol = None
    ):
        from quillion_cli.debug.debugger import debugger

        if path.startswith("http://") or path.startswith("https://"):
            content_message_for_encryption = {
                "action": "redirect",
                "url": path,
            }
            message_to_client = self.crypto.encrypt_response(
                websocket, content_message_for_encryption
            )
            await websocket.send(json.dumps(message_to_client))
            return

        page_cls, params, _ = RouteFinder.find_route(path)

        if page_cls and websocket:
            if not self.current_page or self.current_page.__class__ != page_cls:
                self.current_page = page_cls(params=params or {})
            self.current_path = path
            await self.render_current_page(websocket)
            connection_id = (
                f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            )
            debugger.info(f"[{connection_id}] Redirected to: {path}")
        else:
            connection_id = (
                f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            )
            debugger.error(f"[{connection_id}] Received unknown path: {path}")

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

            if inspect.isawaitable(root_element):
                root_element = await root_element

            from ..components.ui.base.container import Container

            if not isinstance(root_element, Container):
                root_element = Container(root_element)

            page_class_name = self.current_page.get_page_class_name()
            root_element.add_class(page_class_name)

            css_content = ""
            for css_file in self.external_css_files:
                css_content += self._load_css_file(css_file) + "\n"

            style_element = {
                "tag": "style",
                "attributes": {},
                "text": css_content,
                "children": [],
            }

            tree = root_element.to_dict(self)

            content = [style_element, tree]

            self.current_page._cleanup_old_component_instances()
            content_message_for_encryption = {
                "action": "render_page",
                "path": self.current_path,
                "content": content,
            }

            message_to_client = self.crypto.encrypt_response(
                websocket, content_message_for_encryption
            )
            await websocket.send(json.dumps(message_to_client))
        finally:
            self._current_rendering_page = None

    def css(self, files: List[str]):
        self.external_css_files.extend(files)
        return self

    def start(
        self, host="0.0.0.0", port=1337, assets_port=1338, assets_host="localhost"
    ):
        final_host = os.environ.get("QUILLION_HOST", host)
        final_port = int(os.environ.get("QUILLION_PORT", port))
        assets_port = int(os.environ.get("QUILLION_ASSET_PORT", assets_port))
        assets_host = os.environ.get("QUILLION_ASSET_HOST", assets_host)

        self.asset_server_url = f"http://{assets_host}:{assets_port}".rstrip("/")

        self.asset_server.start(host=assets_host, port=assets_port)

        self.server_connection.start(self.handler, final_host, final_port)
