#!/usr/bin/env python3
"""Verify n8n's Turbo and image benchmark plans."""

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)

def main() -> int:
    try:
        plan = tomllib.loads((ROOT / ".boringcache.toml").read_text())
        require(plan["adapters"]["turbo"]["command"] == ["corepack", "pnpm", "build"], "Turbo plan changed")
        docker = plan["adapters"]["docker"]["command"]
        require(docker[:4] == ["bash", "-euo", "pipefail", "-c"], "Docker plan must be argv-safe")
        for fragment in ("24.18.1", "NODE_VERSION", "N8N_VERSION=snapshot", "N8N_RELEASE_TYPE=dev", "--platform linux/amd64", "--sbom true"):
            require(fragment in docker[4], f"Docker plan changed: {fragment}")
        upstream = (ROOT / "upstream/.github/workflows/docker-build-push.yml").read_text()
        for fragment in ("pnpm build:n8n", "NODE_VERSION", "N8N_VERSION", "N8N_RELEASE_TYPE", "sbom: true", "provenance: false"):
            require(fragment in upstream, f"upstream Docker workflow changed: {fragment}")
        docker_action = (ROOT / ".github/actions/n8n-docker-benchmark/action.yml").read_text()
        require(docker_action.count("NODE_VERSION=${{ inputs.node_version }}") == 3, "provider Node arg drifted")
        require(docker_action.count("sbom: true") == 3, "provider SBOM output drifted")
        turbo_action = (ROOT / ".github/actions/n8n-turbo-benchmark/action.yml").read_text()
        require("run-benchmark-plan.py turbo --working-directory upstream" in turbo_action, "Turbo workflow bypasses the plan")
    except (KeyError, OSError, RuntimeError, tomllib.TOMLDecodeError) as error:
        print(f"n8n recipe mismatch: {error}", file=sys.stderr)
        return 1
    print("Verified n8n Turbo and amd64 image plans.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
