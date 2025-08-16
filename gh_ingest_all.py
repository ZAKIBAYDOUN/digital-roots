from __future__ import annotations

"""Utility functions for ingesting files from GitHub repositories.

This module currently exposes a single helper :func:`gather_files` used by
various ingestion scripts.  The original implementation relied on the shell's
brace expansion which is not available on all platforms.  This update adds a
pure Python implementation so the function can understand patterns like
``"**/*.{pdf,docx}"`` or a comma separated list of extensions like
``"pdf,docx"``.
"""

from pathlib import Path
from typing import List, Optional
import re


def _expand_braces(pattern: str) -> List[str]:
    """Recursively expand a brace-style glob pattern.

    Parameters
    ----------
    pattern: str
        A glob pattern that may contain a single set of braces with comma
        separated options, e.g. ``"**/*.{pdf,docx}"``.

    Returns
    -------
    List[str]
        A list of patterns with the brace expression expanded.
    """

    match = re.search(r"\{([^{}]+)\}", pattern)
    if not match:
        return [pattern]

    prefix = pattern[: match.start()]
    suffix = pattern[match.end() :]
    options = match.group(1).split(",")

    expanded: List[str] = []
    for option in options:
        expanded.extend(_expand_braces(f"{prefix}{option}{suffix}"))
    return expanded


def gather_files(
    base_dir: str | Path = ".",
    pattern: Optional[str] = None,
    extensions: Optional[str] = None,
) -> List[Path]:
    """Collect files from ``base_dir`` matching ``pattern`` or ``extensions``.

    The function understands brace-style patterns without relying on shell
    expansion.  Alternatively a comma separated list of file extensions can be
    supplied via ``extensions``.

    Parameters
    ----------
    base_dir: str or Path, optional
        Directory from which to start the search.  Defaults to the current
        directory.
    pattern: str, optional
        Glob pattern relative to ``base_dir``.  Patterns containing brace
        expressions will be expanded in Python.
    extensions: str, optional
        Comma separated list of extensions (``"pdf,docx"`` or
        ``".pdf,.docx"``).  When provided, ``pattern`` is ignored.

    Returns
    -------
    List[Path]
        All matching files.
    """

    if pattern and extensions:
        raise ValueError("Specify either 'pattern' or 'extensions', not both")

    search_patterns: List[str] = []
    if extensions:
        ext_list = [e.strip() for e in extensions.split(",") if e.strip()]
        search_patterns = [f"**/*{ext if ext.startswith('.') else '.' + ext}" for ext in ext_list]
    else:
        pattern = pattern or "**/*"
        search_patterns = _expand_braces(pattern)

    base_path = Path(base_dir)
    files: List[Path] = []
    for p in search_patterns:
        files.extend(f for f in base_path.glob(p) if f.is_file())
    return files


__all__ = ["gather_files"]
