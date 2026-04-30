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
cp -p "${ROOT_DIR}"/rogue*.py "${STAGE_DIR}/"
cp -Rp "${ROOT_DIR}/assets" "${STAGE_DIR}/assets"

(
    cd "${OUT_DIR}"
    pyxel package "${STAGE_DIR}" "${STAGE_DIR}/rogue.py" >/dev/null
    python3 - "${APP_NAME}.pyxapp" <<'PY'
import pathlib
import sys
import zipfile

path = pathlib.Path(sys.argv[1])
tmp_path = path.with_suffix(".tmp")
fixed_date = (1980, 1, 1, 0, 0, 0)

with zipfile.ZipFile(path, "r") as src, zipfile.ZipFile(
    tmp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
) as dst:
    for src_info in sorted(src.infolist(), key=lambda info: info.filename):
        dst_info = zipfile.ZipInfo(src_info.filename, fixed_date)
        dst_info.external_attr = src_info.external_attr
        dst_info.create_system = src_info.create_system
        dst_info.compress_type = zipfile.ZIP_DEFLATED
        dst.writestr(dst_info, src.read(src_info.filename))

tmp_path.replace(path)
PY
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
