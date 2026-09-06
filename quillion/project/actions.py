"""Project creation and management utilities."""

from __future__ import annotations

from pathlib import Path

from .. import cli
from ..templates import INDEX_HTML_TEMPLATE, MAIN_PY_TEMPLATE


def is_quillion_project(path: Path) -> bool:
    """Check if a directory is already a Quillion project."""
    q_dir: Path = path / ".q"
    return q_dir.exists() and (q_dir / "index.html").exists()


def create_q_project(path: Path, app_name: str, force: bool = False) -> None:
    """
    Create a new Quillion project at the given path.

    Args:
        path: Directory path for the project
        app_name: Name of the application (used in title and heading)
        force: If True, overwrite existing Quillion project

    Raises:
        FileExistsError: If project already exists and force is False
    """
    if not force and is_quillion_project(path):
        raise FileExistsError(f"Quillion project already exists at {path}")

    q_dir: Path = path / ".q"
    q_dir.mkdir(parents=True, exist_ok=True)

    index_html: Path = q_dir / "index.html"
    index_html.write_text(INDEX_HTML_TEMPLATE.format(app_name=app_name))

    main_py: Path = path / "main.py"
    if not main_py.exists() or force:
        main_py.write_text(MAIN_PY_TEMPLATE.format(app_name=app_name))
    elif main_py.exists():
        cli.print_err("main.py already exists, keeping existing file")


def init_project(path: Path | None = None, app_name: str = "Quillion App") -> None:
    """
    Initialize Quillion in a directory.

    Args:
        path: Directory to initialize (defaults to current directory)
        app_name: Application name
    """
    target_path: Path = Path.cwd() if path is None else path

    if is_quillion_project(target_path):
        raise FileExistsError(f"Quillion project already exists at {target_path}")

    create_q_project(target_path, app_name, force=False)
