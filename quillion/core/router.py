import asyncio
from typing import Optional, Dict

class Path:
    _app = None

    @classmethod
    def init(cls, app):
        cls._app = app

    @classmethod
    def navigate(cls, to: str, params: Optional[Dict[str, str]] = None):
        if cls._app and cls._app.websocket:
            if params:
                path = to
                for key, value in params.items():
                    path = path.replace(f"{{{key}}}", value)
            else:
                path = to
            asyncio.create_task(cls._app.navigate(path, cls._app.websocket))