"""
Entry point for `python -m quillion`.
"""

import argparse
import importlib.util
import os
import sys
import time

from . import cli
from .app import app
from .var import auto_name_vars


def main() -> None:
    cli.startup_time = time.time()

    if "quillion" not in sys.modules:
        import quillion
        sys.modules.setdefault("quillion", quillion)

    parser = argparse.ArgumentParser(prog="quillion", description="Quillion dev server")
    sub    = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="start the dev server")
    run_p.add_argument("target", help="python file to run")
    run_p.add_argument("--host",      default="localhost")
    run_p.add_argument("--port",      type=int, default=8765, help="WebSocket port")
    run_p.add_argument("--http-port", type=int, default=8080, help="HTTP port")

    args = parser.parse_args()
    if args.command != "run":
        parser.print_help()
        return

    target = os.path.abspath(args.target)
    if not os.path.exists(target):
        cli.print_err(f"file not found: {target}")
        sys.exit(1)

    target_dir = os.path.dirname(target)
    if target_dir not in sys.path:
        sys.path.insert(0, target_dir)

    module_name = os.path.splitext(os.path.basename(target))[0]

    app._is_loading = True
    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None:
        cli.print_err(f"could not load spec for {target}")
        sys.exit(1)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    if spec.loader is None:
        cli.print_err(f"loader is None for {target}")
        sys.exit(1)
    spec.loader.exec_module(mod)
    auto_name_vars(mod)
    app._is_loading = False

    try:
        app.run(host=args.host, port=args.port, http_port=args.http_port, watch=target)
    except KeyboardInterrupt:
        print(f"{cli._C.DIM}shutting down{cli._C.RESET}")


if __name__ == "__main__":
    main()