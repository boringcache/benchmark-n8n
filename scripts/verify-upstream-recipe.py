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
        require(docker[:7] == ["docker", "buildx", "build", "--file", "__N8N_DOCKERFILE__", "--platform", "linux/amd64"], "Docker plan changed")
        for fragment in ("NODE_VERSION=__NODE_VERSION__", "N8N_VERSION=snapshot", "N8N_RELEASE_TYPE=dev", "n8n-benchmark:local"):
            require(fragment in docker, f"Docker plan changed: {fragment}")
        activation = (ROOT / "scripts/activate-docker-plan.py").read_text()
        require('"--push"' in activation and "__N8N_DOCKERFILE__" in activation, "Docker plan activation changed")
        upstream = (ROOT / "upstream/.github/workflows/docker-build-push.yml").read_text()
        for fragment in ("pnpm build:n8n", "NODE_VERSION", "N8N_VERSION", "N8N_RELEASE_TYPE", "--sbom=false", "--provenance=false"):
            require(fragment in upstream, f"upstream Docker workflow changed: {fragment}")
        docker_action = (ROOT / ".github/actions/n8n-docker-benchmark/action.yml").read_text()
        require(docker_action.count("NODE_VERSION=${{ inputs.node_version }}") == 1, "Actions/cache Node arg drifted")
        require(docker_action.count("sbom: false") == 1, "Actions/cache SBOM output drifted")
        require(docker_action.count("Activate the BoringCache Docker plan") == 1, "BoringCache publication projection changed")
        turbo_action = (ROOT / ".github/actions/n8n-turbo-benchmark/action.yml").read_text()
        require("run-benchmark-plan.py turbo --working-directory upstream" in turbo_action, "Turbo workflow bypasses the plan")
    except (KeyError, OSError, RuntimeError, tomllib.TOMLDecodeError) as error:
        print(f"n8n recipe mismatch: {error}", file=sys.stderr)
        return 1
    print("Verified n8n Turbo and amd64 image plans.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
