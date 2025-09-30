import asyncio
import mimetypes
import os
from aiohttp import web

class AssetServer:
    def __init__(self, assets_dir: str = "/"):
        self.assets_dir = assets_dir
        self.app = web.Application()
        self.app.router.add_get("/{path:.*}", self.handle_request)

    async def handle_request(self, request: web.Request) -> web.Response:
        path = request.match_info["path"]
        file_path = os.path.join(self.assets_dir, path)

        if not os.path.abspath(file_path).startswith(os.path.abspath(self.assets_dir)):
            return web.HTTPForbidden()

        if not os.path.isfile(file_path):
            return web.HTTPNotFound()

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        return web.FileResponse(file_path, headers={"Content-Type": mime_type})

    def start(self, host: str = "0.0.0.0", port: int = 1338):
        loop = asyncio.get_event_loop()
        loop.create_task(web._run_app(self.app, host=host, port=port, print=None))