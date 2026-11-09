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
        shutil.rmtree(DIST_ROOT, ignore_errors=True)
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
    modules = DIST_ROOT / "python_modules"
    _prune_unused_aws_service_models(modules)
    _prune_non_runtime_python_artifacts(modules)


def _prune_unused_aws_service_models(python_modules: Path) -> None:
    """Keep Botocore's shared data and S3 model used by django-storages."""
    data_dir = python_modules / "botocore" / "data"
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Botocore service data is missing: {data_dir}")

    s3_model = data_dir / "s3"
    required_shared_data = (
        "_retry.json",
        "endpoints.json",
        "partitions.json",
        "sdk-default-configuration.json",
    )
    missing = [name for name in required_shared_data if not (data_dir / name).is_file()]
    if missing or not s3_model.is_dir():
        raise FileNotFoundError(
            f"Botocore S3 runtime data is incomplete: {', '.join(missing) or s3_model}"
        )

    for path in data_dir.iterdir():
        if path.is_dir() and path.name != "s3":
            shutil.rmtree(path)


def _prune_non_runtime_python_artifacts(python_modules: Path) -> None:
    """Drop generated metadata and source artifacts not needed at runtime."""
    for pattern in ("*.po", "*.mo", "*.pyc", "*.pyo"):
        for path in list(python_modules.rglob(pattern)):
            path.unlink()

    for path in list(python_modules.rglob("__pycache__")):
        if path.is_dir():
            shutil.rmtree(path)

    for path in list(python_modules.rglob("*.dist-info")):
        if path.is_dir():
            shutil.rmtree(path)


if __name__ == "__main__":
    main()
