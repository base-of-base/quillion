"""
Session and its collaborators: SessionState, UpdateManager,
NavigationManager, EventManager, ComponentSerializer.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from . import _context as ctx

if TYPE_CHECKING:
    from .app import App
    from .components.base import Component


@dataclass
class SessionState:
    session_id: str
    values: dict[str, Any] = field(default_factory=dict)
    current_path: str = "/"
    root_component: Component | None = None
    init_sent: bool = False

    def get_var_value(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def set_var_value(self, key: str, value: Any) -> None:
        self.values[key] = value


class UpdateManager:
    def __init__(self, websocket: Any) -> None:
        self._ws = websocket
        self._pending: set[Component] = set()

    def schedule_update(self, comp: Component) -> None:
        self._pending.add(comp)

    async def flush_updates(self, serializer: ComponentSerializer) -> None:
        """Отправляет обновления компонентов, включая изменения детей."""
        if not self._pending:
            return
        
        updates = []
        for comp in self._pending:
            update = {
                "id": comp._id,
                "props": comp.get_props()
            }
            children = comp.get_children()
            if children:
                update["children"] = [serializer.serialize(child, comp._id) for child in children]
            updates.append(update)
        
        self._pending.clear()
        await self._ws.send(json.dumps({"updates": updates}))


class NavigationManager:
    def __init__(
        self,
        routes: dict[str, Callable[[], Component]],
        websocket: Any,
        state: SessionState,
    ) -> None:
        self._routes = routes
        self._ws = websocket
        self._state = state

    async def navigate_to(self, path: str, serializer: ComponentSerializer) -> None:
        if path in self._routes:
            self._state.current_path = path
            page = self._routes[path]()
            self._state.root_component = page
            await self._ws.send(json.dumps({"tree": serializer.serialize(page)}))


class EventManager:
    def __init__(self) -> None:
        self._handlers: dict[str, tuple[Component, str]] = {}

    def register(self, comp: Component, event_name: str) -> str:
        eid = str(uuid.uuid4())[:8]
        self._handlers[eid] = (comp, event_name)
        return eid

    def handle(self, eid: str, event_data: dict[str, Any], session: Session) -> None:
        if eid in self._handlers:
            comp, evt_name = self._handlers[eid]
            try:
                getattr(comp, f"on_{evt_name}")(event_data)
            except Exception:  # noqa: BLE001
                import traceback
                traceback.print_exc()


class ComponentSerializer:
    def __init__(self, event_manager: EventManager) -> None:
        self._events = event_manager

    def serialize(
        self, comp: Component, parent_id: str | None = None
    ) -> dict[str, Any]:
        node: dict[str, Any] = {
            "id": comp._id,
            "tag": comp.tag_name,
            "parent_id": parent_id,
            "props": comp.get_props(),
            "events": {},
            "children": [],
        }
        for evt in comp._event_handlers:
            node["events"][evt] = self._events.register(comp, evt)
        node["children"] = [self.serialize(c, comp._id) for c in comp.get_children()]
        return node


class Session:
    def __init__(self, websocket: Any, app: App) -> None:
        self.ws = websocket
        self.app = app
        self.state = SessionState(session_id=str(uuid.uuid4())[:8])
        self.updater = UpdateManager(websocket)
        self.navigator = NavigationManager(app.routes, websocket, self.state)
        self.events = EventManager()
        self.serializer = ComponentSerializer(self.events)

    async def initialize(self) -> None:
        if self.app.global_css and not self.state.init_sent:
            await self.ws.send(json.dumps({"global_css": self.app.global_css}))
            self.state.init_sent = True
        if "/" in self.app.routes:
            root = self.app.routes["/"]()
            self.state.root_component = root
            await self.ws.send(json.dumps({"tree": self.serializer.serialize(root)}))

    async def hot_reload(self) -> None:
        path = self.state.current_path
        if path not in self.app.routes:
            path = "/"
        if path not in self.app.routes:
            return

        self.events = EventManager()
        self.serializer = ComponentSerializer(self.events)

        token = ctx.current_session.set(self)
        try:
            root = self.app.routes[path]()
            self.state.root_component = root
            await self.ws.send(json.dumps({"tree": self.serializer.serialize(root)}))
        finally:
            ctx.current_session.reset(token)

    async def process_messages(self) -> None:
        async for msg in self.ws:
            token = ctx.current_session.set(self)
            try:
                data = json.loads(msg)
                if data.get("type") == "event":
                    self.events.handle(data.get("event_id"), data.get("data", {}), self)
                    await self.updater.flush_updates(self.serializer)
                elif data.get("type") == "navigate":
                    await self.navigator.navigate_to(data.get("path", "/"), self.serializer)
            except Exception:  # noqa: BLE001
                import traceback
                traceback.print_exc()
            finally:
                ctx.current_session.reset(token)