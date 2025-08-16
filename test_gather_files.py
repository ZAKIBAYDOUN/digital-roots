from pathlib import Path
import tempfile

from gh_ingest_all import gather_files


def _create_files(base: Path, names: list[str]) -> None:
    for name in names:
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


def test_gather_files_brace_pattern() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        _create_files(base, ["one.pdf", "two.docx", "three.txt"])
        result = sorted(p.name for p in gather_files(base, pattern="**/*.{pdf,docx}"))
        assert result == ["one.pdf", "two.docx"]


def test_gather_files_extension_list() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        _create_files(base, ["a.pdf", "b.docx", "c.md"])
        result = sorted(p.name for p in gather_files(base, extensions="pdf,docx"))
        assert result == ["a.pdf", "b.docx"]
