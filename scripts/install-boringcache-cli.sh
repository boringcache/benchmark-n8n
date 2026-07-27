#!/usr/bin/env bash
set -euo pipefail

version="${1:-v1.13.106}"
platform="${2:?usage: install-boringcache-cli.sh vX.Y.Z linux-amd64|linux-arm64}"

[[ "${version}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ || "${version}" == "vcli-canary" ]] || {
  echo "BoringCache version must be vX.Y.Z or vcli-canary, got ${version}" >&2
  exit 1
}
case "${platform}" in
  linux-amd64|linux-arm64) ;;
  *) echo "Unsupported benchmark CLI platform: ${platform}" >&2; exit 1 ;;
esac

asset="boringcache-${platform}"
release_url="https://github.com/boringcache/cli/releases/download/${version}"
download_dir="$(mktemp -d "${RUNNER_TEMP:-/tmp}/boringcache-cli.XXXXXX")"
install_dir="${RUNNER_TEMP:-${HOME}/.local}/boringcache-bin"
trap 'rm -rf "${download_dir}"' EXIT

curl -fsSLo "${download_dir}/${asset}" "${release_url}/${asset}"
curl -fsSLo "${download_dir}/SHA256SUMS" "${release_url}/SHA256SUMS"
(
  cd "${download_dir}"
  grep -F "  ${asset}" SHA256SUMS | sha256sum --check -
)

mkdir -p "${install_dir}"
install -m 0755 "${download_dir}/${asset}" "${install_dir}/boringcache"
echo "${install_dir}" >> "${GITHUB_PATH}"
if [[ "${version}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  "${install_dir}/boringcache" --version | grep -F "${version#v}"
else
  "${install_dir}/boringcache" --version
fi
