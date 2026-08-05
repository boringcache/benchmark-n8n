# BoringCache n8n benchmark

This repository contains the BoringCache benchmark for n8n.

Benchmark workflows are in [`.github/workflows/`](.github/workflows/), with configuration in [`.boringcache.toml`](.boringcache.toml).

The Turbo and Docker workflows build the pinned n8n source on rolling and fresh
runners. `boringcache/one` owns cache setup, restore, save, and evidence; the
workflows retain only n8n source preparation, the real builds, and their
GitHub-cache comparison lanes.
