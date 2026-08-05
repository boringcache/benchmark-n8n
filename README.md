# BoringCache n8n benchmark

This repository contains the BoringCache benchmark for n8n.

Benchmark workflows are in [`.github/workflows/`](.github/workflows/), with configuration in [`.boringcache.toml`](.boringcache.toml).

The Turbo workflows install and build the pinned n8n source on fresh runners.
`boringcache/one` owns remote-cache setup, restore, save, and evidence; this
repository retains the product evidence without reimplementing its correctness
contract.
