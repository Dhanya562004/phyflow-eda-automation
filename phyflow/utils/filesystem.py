"""
Filesystem utilities for PHYFlow.
Provides path validation, directory setup, artifact management, and clean workspace routines.
"""

from pathlib import Path
import shutil
from typing import Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure directory exists and return resolved Path object."""
    p = Path(path).resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def create_run_directory(base_dir: Union[str, Path], run_id: str) -> Path:
    """Create structured run directory layout: runs/<run_id>/{logs, artifacts, reports}."""
    run_path = ensure_dir(Path(base_dir) / run_id)
    ensure_dir(run_path / "logs")
    ensure_dir(run_path / "artifacts")
    ensure_dir(run_path / "reports")
    return run_path


def clean_directory(path: Union[str, Path]) -> None:
    """Recursively clean directory contents if it exists."""
    p = Path(path)
    if p.exists() and p.is_dir():
        shutil.rmtree(p)
