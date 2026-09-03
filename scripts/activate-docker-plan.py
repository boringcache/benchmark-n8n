#!/usr/bin/env python3
"""Resolve matrix and GitHub publication values in the committed Docker plan."""

import argparse
import json
import re
import tomllib
from pathlib import Path, PurePosixPath

PLAN = Path(__file__).resolve().parents[1] / ".boringcache.toml"


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise SystemExit(f"committed n8n plan no longer contains {old!r}")
    return source.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dockerfile", required=True)
    parser.add_argument("--node-version", required=True)
    parser.add_argument("--push", choices=("true", "false"), required=True)
    parser.add_argument("--image", required=True)
    args = parser.parse_args()

    dockerfile = PurePosixPath(args.dockerfile)
    if dockerfile.is_absolute() or ".." in dockerfile.parts or dockerfile.parts[:2] != ("upstream", "docker"):
        raise SystemExit("Dockerfile must stay below upstream/docker")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.node_version):
        raise SystemExit("Node version must be an exact release")

    source = PLAN.read_text()
    source = replace_once(source, '"__N8N_DOCKERFILE__"', json.dumps(args.dockerfile))
    source = replace_once(source, "NODE_VERSION=__NODE_VERSION__", f"NODE_VERSION={args.node_version}")
    if args.push == "true":
        needle = '  "--tag", "n8n-benchmark:local",\n  "upstream",'
        replacement = f'  "--tag", {json.dumps(args.image)},\n  "--push",\n  "upstream",'
        source = replace_once(source, needle, replacement)
    tomllib.loads(source)
    PLAN.write_text(source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
