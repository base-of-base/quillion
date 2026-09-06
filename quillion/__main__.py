"""
Entry point for `python -m quillion`.
"""

import argparse
import importlib
import os
import sys
import time
from pathlib import Path

from . import cli
from .app import app
from .project import create_q_project, init_project
from .var import auto_name_vars


def main() -> None:
    cli.startup_time = time.time()

    if "quillion" not in sys.modules:
        import quillion
        sys.modules.setdefault("quillion", quillion)

    parser = argparse.ArgumentParser(
        prog="quillion",
        description="Quillion - Reactive Web Framework for Python"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    run_p = sub.add_parser("run", help="Start the dev server")
    run_p.add_argument("target", help="Python file to run")
    run_p.add_argument("--host", default="localhost", help="WebSocket host")
    run_p.add_argument("--port", type=int, default=8765, help="WebSocket port")
    run_p.add_argument("--http-port", type=int, default=8080, help="HTTP port")

    new_p = sub.add_parser("new", help="Create a new Quillion project")
    new_p.add_argument("path", help="Path where to create the project")
    new_p.add_argument("--name", default="Quillion App", help="Application name")
    new_p.add_argument("--force", action="store_true", help="Overwrite existing project")

    init_p = sub.add_parser("init", help="Initialize Quillion in current directory")
    init_p.add_argument("--name", default="Quillion App", help="Application name")

    args = parser.parse_args()
    
    if args.command == "new":
        project_path = Path(args.path)
        
        if project_path.exists() and not args.force and project_path.is_dir() and any(project_path.iterdir()):
                cli.print_err(f"Directory is not empty: {project_path}")
                cli.print_info("Use --force to override or choose a different path")
                sys.exit(1)
        
        try:
            project_path.mkdir(parents=True, exist_ok=True)
            create_q_project(project_path, args.name, force=args.force)
            cli.print_ok(f"Quillion project created at {project_path}")
            cli.print_info(f"Run: cd {project_path} && q run main.py")
        except FileExistsError as e:
            cli.print_err(str(e))
            sys.exit(1)
        except Exception as e:  # noqa: BLE001
            cli.print_err(f"Failed to create project: {e}")
            sys.exit(1)

    elif args.command == "init":
        try:
            init_project(app_name=args.name)
            cli.print_ok(f"Quillion project initialized in {Path.cwd()}")
            cli.print_info("Run: q run main.py")
        except FileExistsError as e:
            cli.print_err(str(e))
            sys.exit(1)
        except Exception as e:  # noqa: BLE001
            cli.print_err(f"Failed to initialize project: {e}")
            sys.exit(1)
    
    elif args.command == "run":
        target = os.path.abspath(args.target)
        if not os.path.exists(target):
            cli.print_err(f"File not found: {target}")
            sys.exit(1)

        target_dir = os.path.dirname(target)
        if target_dir not in sys.path:
            sys.path.insert(0, target_dir)

        module_name = os.path.splitext(os.path.basename(target))[0]

        try:
            mod = importlib.import_module(module_name)
        except ImportError as e:
            cli.print_err(f"Could not import module {module_name}: {e}")
            sys.exit(1)

        auto_name_vars(mod)

        app._is_loading = False

        try:
            app.run(
                host=args.host,
                port=args.port,
                http_port=args.http_port,
                watch=target
            )
        except KeyboardInterrupt:
            print(f"{cli._C.DIM}shutting down{cli._C.RESET}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()