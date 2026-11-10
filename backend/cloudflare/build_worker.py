"""Build and dry-run the staged Cloudflare Worker without deploying it."""

import subprocess
import sys
from pathlib import Path

import prepare_app


WORKER_ROOT = Path(__file__).resolve().parent
DIST_ROOT = WORKER_ROOT / "dist"


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "pywrangler", "sync"],
        cwd=WORKER_ROOT,
        check=True,
    )
    prepare_app.main()
    subprocess.run(
        "npx --yes --silent wrangler deploy --dry-run",
        cwd=DIST_ROOT,
        check=True,
        shell=True,
    )


if __name__ == "__main__":
    main()
