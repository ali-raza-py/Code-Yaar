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
and bundles the unpruned `python_modules` directory at the project root.

After reviewing a successful dry-run and configuring the real Hyperdrive
binding, deployment is a separate, manual action from `dist`:

```powershell
Set-Location dist
npx --yes --silent wrangler deploy
```

## Package-size investigation

The original bundle contained 7,172 modules and measured 60,775.47 KiB
uncompressed (15,458.95 KiB gzip). The staged dry-run measured 4,512 modules
and 46,779.18 KiB uncompressed (12,552.06 KiB gzip). This is a reduction
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
that limit. The reported `multipart: message too large [code: 10021]` could not
be confirmed against Cloudflare without an actual deployment, which this build
command intentionally does not perform.
