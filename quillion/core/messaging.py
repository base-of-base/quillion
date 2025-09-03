import websockets
import inspect
import asyncio
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
        elif inner_action == "navigate":
            await self.app.navigate(inner_data.get("path", "/"), websocket)
        elif inner_action == "client_error":
            traceback = inner_data.get("error", "")
            print(f"\n[{websocket.id}] Error occurred")
            print(traceback)
        else:
            print(f"[{websocket.id}] Unknown action: {inner_action}")