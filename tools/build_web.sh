#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT_DIR}/web"
APP_NAME="pyxel-rogue"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/pyxel-rogue-web.XXXXXX")"
STAGE_DIR="${WORK_DIR}/${APP_NAME}"

cleanup() {
    rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

mkdir -p "${STAGE_DIR}" "${OUT_DIR}"
cp "${ROOT_DIR}"/rogue*.py "${STAGE_DIR}/"
cp -R "${ROOT_DIR}/assets" "${STAGE_DIR}/assets"

(
    cd "${OUT_DIR}"
    pyxel package "${STAGE_DIR}" "${STAGE_DIR}/rogue.py"
    pyxel app2html "${APP_NAME}.pyxapp"
    mv "${APP_NAME}.html" index.html
)

python3 - "${OUT_DIR}/index.html" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
text = text.replace('gamepad: "enabled"', 'gamepad: "disabled"')
path.write_text(text, encoding="utf-8")
PY

echo "Wrote ${OUT_DIR}/index.html"
