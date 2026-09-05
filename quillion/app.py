"""
App: the central object that owns routes, sessions, and servers.
"""

from __future__ import annotations
import asyncio
import os
import ast
import __main__ as main_module
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TYPE_CHECKING

from websockets.server import serve

from . import _context as ctx
from .cli import print_banner
from .server import http_handler
from .watcher import watch_and_reload
# Правильные импорты из var.var
from .var.var import _ReactiveVarTransformer, auto_name_vars

if TYPE_CHECKING:
    from .components.base import Component
    from .components.two_way import TwoWayBindingElement
    from .session import Session


class App:
    routes: Dict[str, Callable[[], "Component"]]
    global_css: List[str]
    sessions: Dict[Any, "Session"]
    _is_loading: bool
    _static_dirs: List[Tuple[str, str]]
    _host: str
    _http_port: int
    _ws_port: int

    def __init__(self) -> None:
        self.routes = {}
        self.global_css = []
        self.sessions = {}
        self._is_loading = False
        self._static_dirs = []
        self._host = "localhost"
        self._http_port = 8080
        self._ws_port = 8765

        ctx.quillion_app = self

        q_dir = os.path.join(os.path.dirname(__file__), ".q")
        if os.path.exists(q_dir):
            self._static_dirs.append(("/", q_dir))

    def _index_html_path(self) -> Optional[str]:
        local_path = os.path.join(os.getcwd(), ".q", "index.html")
        return local_path

    def set_default_two_way_component(self, cls: Type["TwoWayBindingElement"]) -> "App":
        ctx.default_two_way_class = cls
        return self

    def css(self, *css_paths: str) -> "App":
        for p in css_paths:
            if isinstance(p, str) and p.endswith(".css") and os.path.exists(p):
                with open(p, encoding="utf-8") as fh:
                    self.global_css.append(fh.read())
            else:
                self.global_css.append(str(p))
        return self

    def static(self, url_prefix: str, directory: str) -> "App":
        prefix = "/" + url_prefix.strip("/") + "/"
        self._static_dirs.append((prefix, os.path.abspath(directory)))
        return self

    def page(self, path: str) -> Callable:
        def decorator(f: Callable[[], "Component"]) -> Callable[[], "Component"]:
            self.routes[path] = f
            return f
        return decorator

    def _ensure_main_transformed(self) -> None:
        """
        Применяет AST‑трансформер к __main__ и перезагружает его глобалы.
        Это нужно, чтобы реактивные присваивания внутри функций работали
        при первом запуске (без hot‑reload).
        """
        if hasattr(main_module, "_reactive_transformed"):
            return

        main_file = getattr(main_module, "__file__", None)
        if not main_file or not main_file.endswith(".py"):
            return
        if not os.path.exists(main_file):
            return

        try:
            with open(main_file, "r", encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source, filename=main_file)
            transformer = _ReactiveVarTransformer()
            transformer.transform(tree)
            ast.fix_missing_locations(tree)
            code = compile(tree, main_file, "exec")

            exec(code, main_module.__dict__)
            main_module._reactive_transformed = True
            auto_name_vars(main_module)

        except Exception as e:
            print(f"[Quillion] Could not apply reactive transform to __main__: {e}")

    async def _delayed_process(self, session: "Session") -> None:
        await session.updater.flush_updates(session.serializer)

    async def _http_handler(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        await http_handler(reader, writer, self._static_dirs, self._index_html_path())

    async def _ws_handler(self, ws: Any, path: Optional[str] = None) -> None:
        from .session import Session as _Session

        session = _Session(ws, self)
        self.sessions[ws] = session
        token = ctx.current_session.set(session)
        try:
            await session.initialize()
            await session.process_messages()
        finally:
            ctx.current_session.reset(token)
            del self.sessions[ws]

    def run(
        self,
        host: str = "localhost",
        port: int = 8765,
        http_port: int = 8080,
        watch: Optional[str] = None,
    ) -> None:
        if self._is_loading:
            return

        # Применяем трансформер к __main__ перед запуском сервера
        self._ensure_main_transformed()

        self._host = host
        self._ws_port = port
        self._http_port = http_port

        async def main() -> None:
            await asyncio.start_server(self._http_handler, host, http_port)
            async with serve(self._ws_handler, host, port):
                print_banner(host, http_port, port, watch or "app")
                if watch:
                    abs_watch = os.path.abspath(watch)
                    module_name = os.path.splitext(os.path.basename(abs_watch))[0]
                    asyncio.create_task(watch_and_reload(self, abs_watch, module_name))
                await asyncio.Future()

        asyncio.run(main())


app = App()
page = app.page