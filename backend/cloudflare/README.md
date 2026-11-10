# Code Yaar Cloudflare Worker

## Build and check the deployment bundle

Run this from `backend/cloudflare`:

```powershell
uv run python build_worker.py
```

The command syncs the production Python dependencies, stages the Django
application, prunes Botocore service data to the S3 model used by R2 storage,
and runs Wrangler's deployment dry-run against `dist`. It does not deploy.
Use the Wrangler `Total Upload` result to check the uncompressed bundle size.

Do not use `uv run pywrangler deploy` for this staged build: PyWrangler syncs
and deploys from the project root's unpruned `python_modules` directory. This
is also true when launched from `dist` with `uv run --project ..`.

In Cloudflare Workers Builds, set the build command to:

```sh
uv sync --locked --all-groups &&
uv run --locked pywrangler sync &&
uv run --locked python prepare_app.py &&
cd dist &&
npx --yes --silent wrangler deploy --dry-run --config wrangler.jsonc
```

Set the deploy command to:

```sh
cd dist && npx --yes --silent wrangler deploy --config wrangler.jsonc
```

The deploy command must invoke Wrangler directly from `dist`; do not wrap it in
PyWrangler or `uv run --project ..`. PyWrangler's deploy hook runs a sync that
restores the full project vendor tree and defeats the staging exclusions.

## Package-size investigation

The original bundle contained 7,172 modules and measured 60,775.47 KiB
uncompressed (15,458.95 KiB gzip). The direct Wrangler dry-run from `dist`
measured 4,512 modules and 46,779.18 KiB uncompressed (12,552.06 KiB gzip).
This is a reduction
of 13,996.29 KiB (23.0%) uncompressed and 2,906.89 KiB (18.8%) gzip.

The primary removable payload was Botocore's service catalog: the full vendor
tree included data for 436 AWS services even though Cloudflare settings use
`django-storages` with the S3 API for R2. The staging step retains Botocore's
shared endpoint data and S3 model. Pillow, ReportLab, qrcode, Boto3, and the
S3-related dependencies remain because they support existing image, PDF,
certificate, and object-storage behavior. PyWrangler's development dependency
group is not installed into the production vendor directory.

Cloudflare's current Workers limits documentation lists a 64 MiB uncompressed
Worker-size limit and no compressed-size limit. The staged bundle is below
that limit. PyWrangler's deploy command bypasses the staging exclusions, which
is why deployment still uploaded 60,775 KiB despite the successful staged
dry-run. The corrected deploy command uses Wrangler directly so it uploads
the staged bundle.
