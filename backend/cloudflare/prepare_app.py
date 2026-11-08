"""Stage the existing Django project alongside Pywrangler's vendored packages."""

import shutil
from pathlib import Path


WORKER_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = WORKER_ROOT.parent
VENDOR_ROOT = WORKER_ROOT / "python_modules"
DIST_ROOT = WORKER_ROOT / "dist"
APP_DIRECTORIES = ("config", "learning", "certificates", "branding", "templates")
APP_FILES = ("branding.py",)


def main() -> None:
    for name in APP_DIRECTORIES:
        source = BACKEND_ROOT / name
        destination = VENDOR_ROOT / name
        if not source.is_dir():
            raise FileNotFoundError(f"Required Django application directory is missing: {source}")
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.py[cod]", "tests.py", "tests_*.py"),
        )

    for name in APP_FILES:
        source = BACKEND_ROOT / name
        destination = VENDOR_ROOT / name
        if not source.is_file():
            raise FileNotFoundError(f"Required Django application module is missing: {source}")
        shutil.copy2(source, destination)

    if DIST_ROOT.exists():
        shutil.rmtree(DIST_ROOT)
    DIST_ROOT.mkdir()
    shutil.copy2(WORKER_ROOT / "worker.py", DIST_ROOT / "worker.py")
    shutil.copy2(WORKER_ROOT / "wrangler.jsonc", DIST_ROOT / "wrangler.jsonc")
    shutil.copytree(
        VENDOR_ROOT,
        DIST_ROOT / "python_modules",
        ignore=shutil.ignore_patterns(
            "pyvenv.cfg", ".synced", "__pycache__", "*.py[cod]"
        ),
    )


if __name__ == "__main__":
    main()
