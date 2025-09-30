import asyncio
import websockets
from typing import Callable


class ServerConnection:
    def start(self, handler: Callable, host: str = "0.0.0.0", port: int = 1337):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(websockets.serve(handler, host, port))
        loop.run_forever()
