#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pyxel-rogue-check-web.XXXXXX")"

cleanup() {
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

git -C "${ROOT_DIR}" diff -- web/index.html > "${WORK_DIR}/before-index.diff"
if git -C "${ROOT_DIR}" ls-files --error-unmatch web/pyxel-rogue.pyxapp >/dev/null 2>&1; then
    git -C "${ROOT_DIR}" diff -- web/pyxel-rogue.pyxapp > "${WORK_DIR}/before-pyxapp.diff"
fi

"${ROOT_DIR}/tools/build_web.sh"

git -C "${ROOT_DIR}" diff -- web/index.html > "${WORK_DIR}/after-index.diff"
diff -u "${WORK_DIR}/before-index.diff" "${WORK_DIR}/after-index.diff"

if git -C "${ROOT_DIR}" ls-files --error-unmatch web/pyxel-rogue.pyxapp >/dev/null 2>&1; then
    git -C "${ROOT_DIR}" diff -- web/pyxel-rogue.pyxapp > "${WORK_DIR}/after-pyxapp.diff"
    diff -u "${WORK_DIR}/before-pyxapp.diff" "${WORK_DIR}/after-pyxapp.diff"
elif [[ ! -f "${ROOT_DIR}/web/pyxel-rogue.pyxapp" ]]; then
    echo "Missing web/pyxel-rogue.pyxapp" >&2
    exit 1
fi

echo "Web build is up to date."
