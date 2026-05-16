# TravelMate — Build & Run Guide

This README documents how to build and run TravelMate on supported platforms, troubleshooting tips, and the key commands used during development.

## Prerequisites
- Python 3.8+ (3.14 tested in this workspace)
- `pip` available (use the `py` launcher on Windows)
- Recommended: create and use a virtual environment

## Install dependencies
On Windows (PowerShell):

```powershell
py -m pip install -r requirements.txt
```

If `py` is not available, use your Python executable (e.g. `python -m pip install -r requirements.txt`).

## Build (single-file executable)
The project provides `build.py` which wraps PyInstaller. To build a single-file Windows executable:

```powershell
py build.py
```

Options supported by `build.py`:
- `--mode onefile` (default) — produces a single `.exe` in `dist/`
- `--mode onedir` — produces an application folder
- `--os windows` — target OS (defaults to `windows` on Windows hosts)

Examples:

```powershell
# One-file build (default)
py build.py

# One-dir build
py build.py --mode onedir
```

For cross-compiling Windows binaries on Linux/macOS, a Docker image (`cdrx/pyinstaller-windows`) is used by `build.py` when available.

## Run built executable
After building, the single executable is in `dist/TravelMate_v<version>.exe`.

Double-click it in Explorer or run from PowerShell:

```powershell
.\dist\TravelMate_v1.0.0.exe
```

## Common issues & fixes
- ModuleNotFoundError for `nltk`: ensure `nltk` is installed in the Python used to build the app. Run `py -m pip install -r requirements.txt` before building.
- NLTK data path: `nltk_data` is bundled and the engine sets `nltk.data.path` to the extracted resources at runtime.
- Encoding errors when loading `intents.json`: files are opened with `encoding='utf-8'` to avoid `charmap` decoding errors on some systems.
- Database initialization: the app now ensures the SQLite database file is created before GUI startup. The database is stored in `%APPDATA%/TravelMate/chatbot.db` on Windows, or `~/.travelmate/chatbot.db` on Linux/macOS.

## Development & tests
Run unit tests with:

```powershell
py -m pytest tests
```

## Notes
- If PyInstaller scripts are installed but not on PATH, use `py -m PyInstaller` or the `build.py` helper which already calls PyInstaller via `sys.executable -m PyInstaller`.
- For reproducible builds, ensure the same Python minor version and package versions are used.

If you want, I can: rebuild the executable now, or produce a portable build using `--mode onedir`.
