"""Stage the existing Django project alongside Pywrangler's vendored packages."""

import shutil
from uuid import UUID
from pathlib import Path

import pyjson5


WORKER_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = WORKER_ROOT.parent
VENDOR_ROOT = WORKER_ROOT / "python_modules"
DIST_ROOT = WORKER_ROOT / "dist"
APP_DIRECTORIES = ("config", "learning", "certificates", "branding", "templates")
APP_FILES = ("branding.py",)


def main() -> None:
    source_config = WORKER_ROOT / "wrangler.jsonc"
    source_hyperdrive_id = _validate_hyperdrive_config(source_config)

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
    staged_config = DIST_ROOT / "wrangler.jsonc"
    shutil.copy2(source_config, staged_config)
    staged_hyperdrive_id = _validate_hyperdrive_config(staged_config)
    if staged_hyperdrive_id != source_hyperdrive_id:
        raise ValueError("Staged Hyperdrive ID does not match the source Wrangler config")

    _validate_botocore_s3_data(VENDOR_ROOT)
    shutil.copytree(
        VENDOR_ROOT,
        DIST_ROOT / "python_modules",
        ignore=_ignore_non_runtime_python_artifacts,
    )


def _validate_hyperdrive_config(config_path: Path) -> str:
    with config_path.open(encoding="utf-8") as config_file:
        config = pyjson5.decode_io(config_file)

    if not isinstance(config, dict):
        raise ValueError(f"Wrangler config must be an object: {config_path}")

    bindings = config.get("hyperdrive")
    if not isinstance(bindings, list):
        raise ValueError(f"Wrangler config must define a Hyperdrive binding: {config_path}")

    binding_ids = [
        binding.get("id")
        for binding in bindings
        if isinstance(binding, dict) and binding.get("binding") == "HYPERDRIVE"
    ]
    if len(binding_ids) != 1 or not isinstance(binding_ids[0], str):
        raise ValueError(f"Wrangler config must define exactly one HYPERDRIVE ID: {config_path}")

    hyperdrive_id = binding_ids[0]
    try:
        UUID(hyperdrive_id)
    except ValueError as error:
        raise ValueError(
            f"Invalid HYPERDRIVE ID in {config_path}: {hyperdrive_id!r}; "
            "use the ID of an existing Cloudflare Hyperdrive configuration"
        ) from error

    print(f"Validated HYPERDRIVE ID {hyperdrive_id} in {config_path}")
    return hyperdrive_id


def _validate_botocore_s3_data(python_modules: Path) -> None:
    """Require the shared Botocore data and S3 model used by django-storages."""
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


def _ignore_non_runtime_python_artifacts(directory: str, names: list[str]) -> set[str]:
    ignored = {
        name
        for name in names
        if name in {"__pycache__", ".synced", "pyvenv.cfg"}
        or name.endswith((".dist-info", ".po", ".mo", ".pyc", ".pyo", ".pyd"))
    }

    if Path(directory) == VENDOR_ROOT / "botocore" / "data":
        ignored.update(
            name
            for name in names
            if name != "s3" and (VENDOR_ROOT / "botocore" / "data" / name).is_dir()
        )

    return ignored


if __name__ == "__main__":
    main()
