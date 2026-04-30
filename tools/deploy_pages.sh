#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE="${1:-origin}"
BRANCH="${2:-gh-pages}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pyxel-rogue-pages.XXXXXX")"
PAGES_DIR="${WORK_DIR}/${BRANCH}"

cleanup() {
    git -C "${ROOT_DIR}" worktree remove --force "${PAGES_DIR}" >/dev/null 2>&1 || true
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

"${ROOT_DIR}/tools/build_web.sh"

if git -C "${ROOT_DIR}" ls-remote --exit-code --heads "${REMOTE}" "${BRANCH}" >/dev/null 2>&1; then
    git -C "${ROOT_DIR}" fetch "${REMOTE}" "${BRANCH}"
    git -C "${ROOT_DIR}" worktree add -B "${BRANCH}" "${PAGES_DIR}" "${REMOTE}/${BRANCH}"
else
    mkdir -p "${PAGES_DIR}"
    git -C "${ROOT_DIR}" worktree add --detach "${PAGES_DIR}"
    git -C "${PAGES_DIR}" checkout --orphan "${BRANCH}"
fi

git -C "${PAGES_DIR}" rm -r --ignore-unmatch . >/dev/null 2>&1 || true

cp "${ROOT_DIR}/web/index.html" "${PAGES_DIR}/index.html"
if [[ -f "${ROOT_DIR}/web/pyxel-rogue.pyxapp" ]]; then
    cp "${ROOT_DIR}/web/pyxel-rogue.pyxapp" "${PAGES_DIR}/pyxel-rogue.pyxapp"
fi
touch "${PAGES_DIR}/.nojekyll"

git -C "${PAGES_DIR}" add index.html .nojekyll
if [[ -f "${PAGES_DIR}/pyxel-rogue.pyxapp" ]]; then
    git -C "${PAGES_DIR}" add pyxel-rogue.pyxapp
fi

if git -C "${PAGES_DIR}" diff --cached --quiet; then
    echo "No Pages changes to deploy."
    exit 0
fi

git -C "${PAGES_DIR}" commit -m "Deploy Pyxel Web build"
git -C "${PAGES_DIR}" push "${REMOTE}" "${BRANCH}"

echo "Deployed GitHub Pages branch: ${BRANCH}"
