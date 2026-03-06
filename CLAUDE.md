# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SortPhotos is a Python 3.9+ CLI tool that sorts photos and videos into date-based directory hierarchies using EXIF metadata. It wraps a vendored copy of ExifTool (Perl) to extract timestamps from media files.

## Running

```bash
# Install in a virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run directly
python src/sortphotos.py <source_dir> <dest_dir>

# Run after install
sortphotos <source_dir> <dest_dir>

# Dry run (simulate without moving/copying)
sortphotos -t <source_dir> <dest_dir>
```

**Requires Perl** — ExifTool is a Perl application vendored at `src/Image-ExifTool/`.

## Testing

```bash
pytest              # run all tests
pytest tests/test_sortphotos.py::TestParseDateExif  # run one test class
pytest -k "test_basic_datetime"                      # run by name
```

Tests use `unittest.mock` to patch `ExifTool` for integration tests, avoiding the need for perl in CI. The ExifTool context manager test is skipped if perl is not available.

## Architecture

Single-file application (`src/sortphotos.py`) with these key components:

- **`ExifTool` class** — Context manager that keeps a persistent ExifTool subprocess open. Communicates via stdin/stdout with JSON output.
- **`parse_date_exif()`** — Parses EXIF date strings (`YYYY:MM:DD HH:MM:SS`) including timezone offsets into `datetime` objects.
- **`get_oldest_timestamp()`** — Iterates all metadata tags for a file, filters by ignore/use-only rules, and returns the oldest valid date.
- **`sortPhotos()`** — Core engine: extracts metadata, builds destination paths using `strftime`, handles duplicates via `filecmp.cmp`, collects file transfers, then executes them (optionally in parallel with `--jobs`). Returns a stats dict.
- **`_transfer_file()`** — Helper for moving/copying a single file with error handling. Used by both serial and parallel code paths.
- **`main()`** — CLI entry point with argparse. Configures logging levels.

**Data flow:** CLI args → ExifTool extracts all timestamps (JSON) → oldest date per file → destination path via `strftime(sort_format)` → collision/duplicate check → collect transfers → execute (serial or parallel) → print summary stats.

## Key Details

- Python 3.9+ required. Uses `pathlib`, type hints, f-strings throughout.
- Runtime dependency: `tqdm` (progress bar). Dev dependency: `pytest`.
- Uses `logging` module — levels controlled by `--verbose` (DEBUG), default (INFO), `--quiet`/`--silent` (WARNING).
- ExifTool path auto-resolved: `Path(__file__).resolve().parent / 'Image-ExifTool' / 'exiftool'`
- Default sort format: `%Y/%m-%b` (e.g., `2024/02-Feb/`)
- Forward slashes in `--sort` format create subdirectories
- Hidden files (dotfiles) are automatically skipped
- `ICC_Profile` group and `XMP:HistoryWhen` tag are always ignored for date extraction
- The `File` tag group is ignored by default (contains filesystem timestamps, not EXIF data)
- Duplicate detection compares both filename and file content via `filecmp.cmp`
- `--exclude` patterns use `fnmatch` for glob-style filtering
- `--jobs N` enables parallel file transfers via `ThreadPoolExecutor`
- Build config is in `pyproject.toml` (no setup.py)
