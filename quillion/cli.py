"""
Terminal output: colours, banner, reload messages.
"""

from __future__ import annotations
import sys
import time
from typing import Optional


class _C:
    """ANSI colour codes."""
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    CYAN     = "\033[36m"
    GREEN    = "\033[32m"
    YELLOW   = "\033[33m"
    RED      = "\033[31m"
    WHITE    = "\033[97m"
    MAGENTA  = "\033[35m"
    BG_GREEN = "\033[42m"
    BLACK    = "\033[30m"

    @staticmethod
    def supported() -> bool:
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _clr(code: str, text: str) -> str:
    return f"{code}{text}{_C.RESET}" if _C.supported() else text


startup_time: Optional[float] = None


def print_banner(host: str, http_port: int, ws_port: int, target: str) -> None:
    c = _C.supported()
    badge = _clr(_C.BG_GREEN + _C.BLACK + _C.BOLD, " q ") if c else "[q]"
    url   = f"http://{host}:{http_port}"

    if startup_time is not None:
        elapsed = time.time() - startup_time
        if elapsed < 1:
            time_str = f"{elapsed * 1000:.0f}ms"
        elif elapsed < 60:
            time_str = f"{elapsed:.2f}s"
        else:
            m = int(elapsed // 60)
            time_str = f"{m}m {elapsed % 60:.0f}s"
    else:
        time_str = "—"

    print()
    print(f"  {badge}  {_clr(_C.WHITE + _C.BOLD, 'quillion')}")
    print()
    print(f"  {_clr(_C.DIM, 'local')}    {_clr(_C.GREEN, url)}")
    print(f"  {_clr(_C.DIM, 'ws')}       {_clr(_C.GREEN, f'ws://{host}:{ws_port}')}")
    print()
    print(
        f"  {_clr(_C.DIM, 'ready in')} {_clr(_C.GREEN, time_str)}"
    )
    print()


def print_reload(filename: str, elapsed_ms: float) -> None:
    tag  = _clr(_C.GREEN + _C.BOLD, "~") if _C.supported() else "~"
    name = _clr(_C.WHITE, filename)
    ms   = _clr(_C.DIM, f"{elapsed_ms:.1f}ms")
    print(f"  {tag}  {name}  {ms}")


def print_reload_err(err: Exception) -> None:
    tag = _clr(_C.RED + _C.BOLD, "x") if _C.supported() else "x"
    print(f"  {tag}  {_clr(_C.RED, str(err))}")


def print_err(msg: str) -> None:
    tag = _clr(_C.RED + _C.BOLD, "error") if _C.supported() else "error"
    print(f"  {tag}  {msg}")
