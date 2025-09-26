import websockets
import inspect
import json
from typing import Dict, Any


class Messaging:
    def __init__(self, app):
        self.app = app

    async def process_inner_message(
        self, websocket: websockets.WebSocketServerProtocol, inner_data: Dict[str, Any]
    ):
        inner_action = inner_data.get("action")

        if inner_action == "callback":
            cb_id = inner_data.get("id")
            if cb_id in self.app.callbacks:
                cb = self.app.callbacks[cb_id]
                result = cb()
                if inspect.isawaitable(result):
                    await result
                await self.app.render_current_page(websocket)
                
        elif inner_action == "event_callback":
            cb_id = inner_data.get("id")
            event_data_str = inner_data.get("event_data", "{}")
            
            if cb_id in self.app.callbacks:
                cb = self.app.callbacks[cb_id]
                
                try:
                    event_data = json.loads(event_data_str) if event_data_str else {}
                except json.JSONDecodeError:
                    event_data = {}
                
                sig = inspect.signature(cb)
                if len(sig.parameters) > 0:
                    result = cb(event_data)
                else:
                    result = cb()
                
                if inspect.isawaitable(result):
                    await result
                await self.app.render_current_page(websocket)
                
        elif inner_action == "navigate":
            await self.app.navigate(inner_data.get("path", "/"), websocket)
        elif inner_action == "client_error":
            traceback = inner_data.get("error", "")
            print(f"\n[{websocket.remote_address[0]}:{websocket.remote_address[1]}] Error occurred")
            print(traceback)
        else:
            print(f"[{websocket.remote_address[0]}:{websocket.remote_address[1]}] Unknown action: {inner_action}")
