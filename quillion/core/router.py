import asyncio
from typing import Optional


class Path:
    _app = None

    @classmethod
    def init(cls, app):
        cls._app = app

    @classmethod
    def navigate(cls, to: str):
        if cls._app:
            asyncio.create_task(cls._app.navigate(to, cls._app.websocket))
