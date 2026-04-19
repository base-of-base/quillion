"""
Static file handler and raw HTTP/1.1 server.
"""

from __future__ import annotations
import asyncio
import mimetypes
import os
from typing import Any, Callable, List, Optional, Tuple, Union
from urllib.parse import unquote

from .cli import print_err


_STATIC_EXTENSIONS = {
    ".js",
    ".css",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".map",
    ".json",
    ".xml",
    ".txt",
    ".pdf",
    ".webp",
    ".mp4",
    ".webm",
    ".mp3",
    ".wav",
}


class StaticFileHandler:
    def __init__(self, static_dirs: List[Tuple[str, str]]) -> None:
        self.static_dirs = static_dirs

    def find_file(self, path: str) -> Optional[Tuple[str, str]]:
        """Return (absolute_file_path, mime_type) or None."""
        path = unquote(path)
        for url_prefix, fs_dir in self.static_dirs:
            if not path.startswith(url_prefix):
                continue
            relative = path[len(url_prefix) :].lstrip("/") or "index.html"
            file_path = os.path.normpath(os.path.join(fs_dir, relative))
            if not file_path.startswith(os.path.normpath(fs_dir)):
                continue
            if os.path.isfile(file_path):
                mime, _ = mimetypes.guess_type(file_path)
                return file_path, mime or "application/octet-stream"
        return None

    async def serve(
        self,
        path: str,
        send_response: Callable[[int, Union[str, bytes], Optional[str]], Any],
    ) -> bool:
        result = self.find_file(path)
        if result is None:
            return False
        file_path, mime = result
        with open(file_path, "rb") as fh:
            content = fh.read()
        await send_response(200, content, mime)
        return True


def is_static_path(path: str) -> bool:
    return any(path.lower().endswith(ext) for ext in _STATIC_EXTENSIONS)


async def http_handler(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    static_dirs: List[Tuple[str, str]],
    index_html_path: Optional[str],
) -> None:
    try:
        request_line = await reader.readline()
        if not request_line:
            writer.close()
            return

        parts = request_line.decode().split()
        if len(parts) < 2:
            writer.close()
            return

        method, path = parts[0], parts[1].split("?")[0]

        async def send(
            status: int, content: Union[str, bytes], ct: Optional[str] = "text/html"
        ) -> None:
            if isinstance(content, str):
                content = content.encode("utf-8")
            writer.write(f"HTTP/1.1 {status}\r\n".encode())
            writer.write(f"Content-Type: {ct}\r\n".encode())
            writer.write(f"Content-Length: {len(content)}\r\n".encode())
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(content)
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        if method != "GET":
            await send(405, b"")
            return

        handler = StaticFileHandler(static_dirs)
        if await handler.serve(path, send):
            return

        if is_static_path(path):
            await send(404, b"Not Found", None)
            return

        if index_html_path and os.path.exists(index_html_path):
            with open(index_html_path, "rb") as fh:
                await send(200, fh.read(), "text/html")
            return

        await send(404, b"Not Found", None)

    except Exception as exc:
        print_err(f"http: {exc}")
        try:
            writer.close()
        except Exception:
            pass
