# benchmark-n8n

Public n8n benchmark runner for BoringCache vs GitHub Actions cache.

This repo exists separately from [`boringcache/benchmarks`](https://github.com/boringcache/benchmarks) so the benchmark keeps:

- one pinned upstream source commit
- isolated GitHub Actions cache usage
- one per-repo BoringCache workspace name: `boringcache/benchmark-n8n`
- independent workflow history plus upstream-sync-driven benchmark runs and manual dispatches

## Source Model

- Upstream source lives in the pinned `upstream/` submodule.

Pinned upstream source:

- see committed `upstream/` submodule on `main`

## What It Measures

Fresh lane runs a no-prior-cache cold build plus one warm rerun for each backend:

- `cold`
- `warm1`

Rolling lane records the upstream commit build as-is after each upstream sync against the prior rolling cache and intentionally skips `warm1`.

The benchmark has two tool-specific surfaces:

- `n8n`: Turbo build for the pnpm monorepo.
- `n8n-docker`, `n8n-runners`, and `n8n-runners-distroless`: BuildKit builds for the three Docker images n8n publishes. These lanes prepare the n8n build artifacts before the measured Docker build, so the timed section isolates Docker layer/cache behavior rather than rerunning the Turbo benchmark inside the Docker lane.

Scheduled, PR, and rolling-dispatch Docker runs use [`.github/workflows/n8n-docker-benchmark.yml`](.github/workflows/n8n-docker-benchmark.yml), which runs GitHub Actions Cache, BoringCache OCI, and BoringCache Auto side by side for all three images. The provider-specific Docker workflows remain for manual diagnostics.

The story this benchmark is meant to show is:

- speed on fresh cold and warm paths
- commit-build behavior on normal upstream syncs in the rolling lane
- storage footprint in each backend
- whether Turbo and BuildKit cache reuse stay reliable on fresh runners

## Token Model

This repo uses split BoringCache tokens as the standard CI shape:

- `BORINGCACHE_RESTORE_TOKEN` for read-only restore and proxy access
- `BORINGCACHE_SAVE_TOKEN` for trusted write paths
- `BORINGCACHE_API_TOKEN` only where a single bearer variable is still required for compatibility
