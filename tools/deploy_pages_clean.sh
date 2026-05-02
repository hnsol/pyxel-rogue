#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

"${ROOT_DIR}/tools/deploy_pages.sh" "$@"
git -C "${ROOT_DIR}" restore web/index.html
