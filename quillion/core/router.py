import asyncio
from typing import Optional, Dict


class Path:
    _app = None

    @classmethod
    def init(cls, app):
        cls._app = app

    @classmethod
    def navigate(cls, to: str, params: Optional[Dict[str, str]] = None):
        if not cls._app or not cls._app.websocket:
            return
            
        path = to.format(**params) if params else to
        asyncio.create_task(cls._app.navigate(path, cls._app.websocket))
