"""
Session and its collaborators: SessionState, UpdateManager,
NavigationManager, EventManager, ComponentSerializer.
"""

from __future__ import annotations
import asyncio
import json
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Set, Tuple, TYPE_CHECKING

from . import _context as ctx

if TYPE_CHECKING:
    from .components.base import Component
    from .app import App


@dataclass
class SessionState:
    session_id: str
    values: Dict[str, Any] = field(default_factory=dict)
    current_path: str = "/"
    root_component: Optional["Component"] = None
    init_sent: bool = False

    def get_var_value(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)

    def set_var_value(self, key: str, value: Any) -> None:
        self.values[key] = value


class UpdateManager:
    def __init__(self, websocket: Any) -> None:
        self._ws = websocket
        self._pending: Set["Component"] = set()

    def schedule_update(self, comp: "Component") -> None:
        self._pending.add(comp)

    async def flush_updates(self, serializer: "ComponentSerializer") -> None:
        if not self._pending:
            return
        updates = [{"id": c._id, "props": c.get_props()} for c in self._pending]
        self._pending.clear()
        await self._ws.send(json.dumps({"updates": updates}))


class NavigationManager:
    def __init__(
        self,
        routes: Dict[str, Callable[[], "Component"]],
        websocket: Any,
        state: SessionState,
    ) -> None:
        self._routes = routes
        self._ws = websocket
        self._state = state

    async def navigate_to(self, path: str, serializer: "ComponentSerializer") -> None:
        if path in self._routes:
            self._state.current_path = path
            page = self._routes[path]()
            self._state.root_component = page
            await self._ws.send(json.dumps({"tree": serializer.serialize(page)}))


class EventManager:
    def __init__(self) -> None:
        self._handlers: Dict[str, Tuple["Component", str]] = {}

    def register(self, comp: "Component", event_name: str) -> str:
        eid = str(uuid.uuid4())[:8]
        self._handlers[eid] = (comp, event_name)
        return eid

    def handle(self, eid: str, event_data: Dict[str, Any], session: "Session") -> None:
        if eid in self._handlers:
            comp, evt_name = self._handlers[eid]
            getattr(comp, f"on_{evt_name}")(event_data)


class ComponentSerializer:
    def __init__(self, event_manager: EventManager) -> None:
        self._events = event_manager

    def serialize(self, comp: "Component", parent_id: Optional[str] = None) -> Dict[str, Any]:
        node: Dict[str, Any] = {
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
    def __init__(self, websocket: Any, app: "App") -> None:
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
            data = json.loads(msg)
            if data.get("type") == "event":
                self.events.handle(data.get("event_id"), data.get("data", {}), self)
                await self.updater.flush_updates(self.serializer)
            elif data.get("type") == "navigate":
                await self.navigator.navigate_to(data.get("path", "/"), self.serializer)
