"""
File watcher: polls for changes and triggers hot-reload on all sessions.
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import importlib
import logging
import os
import sys
import time
import traceback
from typing import TYPE_CHECKING

from .. import _context as ctx
from ..cli import _C, _clr, print_reload
from ..var import auto_name_vars

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..app import App


def file_hash(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()
    except FileNotFoundError:
        return ""


def _is_local_file(file_path: str) -> bool:
    try:
        abs_path = os.path.abspath(file_path)
        for site_packages_dir in sys.path:
            if (
                "site-packages" in site_packages_dir
                or "dist-packages" in site_packages_dir
            ) and abs_path.startswith(os.path.abspath(site_packages_dir)):
                return False
        std_lib_dir = os.path.dirname(os.__file__)
        if abs_path.startswith(std_lib_dir):
            return False
        return os.path.exists(abs_path) and abs_path.endswith(".py")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error checking local file %s: %s", file_path, exc)
        return False


def _extract_imports(file_path: str) -> set[str]:
    imports: set[str] = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to extract imports from %s: %s", file_path, exc)
    return imports


def _find_module_file(module_name: str, base_path: str) -> str | None:
    base_dir = os.path.dirname(base_path)
    possible_paths: list[str] = [
        os.path.join(base_dir, f"{module_name}.py"),
        os.path.join(base_dir, module_name, "__init__.py"),
        os.path.join(base_dir, f"{module_name.replace('.', os.sep)}.py"),
        os.path.join(base_dir, *module_name.split("."), "__init__.py"),
    ]
    for path in possible_paths:
        if os.path.exists(path) and _is_local_file(path):
            return path
    return None


def _get_dependent_files(target_path: str) -> set[str]:
    dependent_files: set[str] = set()
    processed: set[str] = set()

    def collect(file_path: str) -> None:
        abs_path = os.path.abspath(file_path)
        if abs_path in processed:
            return
        processed.add(abs_path)

        if _is_local_file(abs_path):
            dependent_files.add(abs_path)
            imports = _extract_imports(abs_path)
            for module_name in imports:
                module_file = _find_module_file(module_name, abs_path)
                if module_file and module_file not in processed:
                    collect(module_file)

    collect(target_path)
    return dependent_files


class _FileWatcher:
    target_path: str
    app: App
    module_name: str
    file_hashes: dict[str, str]
    watched_files: set[str]
    last_changed_file: str | None

    def __init__(self, target_path: str, app: App, module_name: str) -> None:
        self.target_path = os.path.abspath(target_path)
        self.app = app
        self.module_name = module_name
        self.file_hashes: dict[str, str] = {}
        self.watched_files: set[str] = set()
        self.last_changed_file: str | None = None

    async def _update_watched_files(self) -> None:
        new_files = _get_dependent_files(self.target_path)
        for file_path in new_files:
            if file_path not in self.watched_files:
                self.watched_files.add(file_path)
                self.file_hashes[file_path] = file_hash(file_path)
        for file_path in list(self.watched_files):
            if file_path not in new_files:
                del self.file_hashes[file_path]
                self.watched_files.remove(file_path)

    async def _has_changes(self) -> bool:
        await self._update_watched_files()
        for file_path in self.watched_files:
            current_hash = file_hash(file_path)
            if current_hash != self.file_hashes.get(file_path, ""):
                self.file_hashes[file_path] = current_hash
                self.last_changed_file = file_path
                return True
        self.last_changed_file = None
        return False

    async def _reload(self) -> None:
        t0: float = time.perf_counter()
        try:
            self.app._is_loading = True

            modules_to_reload: set[str] = set()
            changed_module_name: str | None = None

            for file_path in self.watched_files:
                for name, module in sys.modules.items():
                    if (hasattr(module, "__file__") and module.__file__
                            and os.path.abspath(module.__file__) == file_path):
                        modules_to_reload.add(name)
                        if file_path == self.last_changed_file:
                            changed_module_name = name
                        break

            for module_name in sorted(modules_to_reload):
                if module_name in sys.modules:
                    try:
                        importlib.reload(sys.modules[module_name])
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Failed to reload module %s: %s", module_name, exc)

            if self.module_name in sys.modules:
                importlib.reload(sys.modules[self.module_name])
                if changed_module_name is None:
                    changed_module_name = self.module_name

            auto_name_vars(sys.modules[self.module_name])
            self.app._is_loading = False

            sessions = list(self.app.sessions.values())
            for s in sessions:
                token = ctx.current_session.set(s)
                try:
                    await s.hot_reload()
                finally:
                    ctx.current_session.reset(token)

            elapsed_ms: float = (time.perf_counter() - t0) * 1000

            if changed_module_name:
                changed_file = self.last_changed_file
                if changed_file:
                    filename = os.path.basename(changed_file)
                else:
                    filename = f"{changed_module_name}.py"
            else:
                filename = os.path.basename(self.target_path)

            print_reload(filename, elapsed_ms)

        except Exception as exc:  # noqa: BLE001
            elapsed_ms = (time.perf_counter() - t0) * 1000
            tag = _clr(_C.RED + _C.BOLD, "x") if _C.supported() else "x"
            ms = _clr(_C.DIM, f"{elapsed_ms:.1f}ms")
            logger.error("Reload failed: %s", exc)
            print(f"  {tag}  {_clr(_C.RED, str(exc))}  {ms}")
            traceback.print_exc()
            self.app._is_loading = False

    async def watch(self) -> None:
        await self._update_watched_files()
        while True:
            await asyncio.sleep(0.3)
            if await self._has_changes():
                await self._reload()


async def watch_and_reload(app: App, target_path: str, module_name: str) -> None:
    watcher = _FileWatcher(target_path, app, module_name)
    await watcher.watch()
