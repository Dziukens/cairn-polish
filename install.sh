#!/usr/bin/env bash
# Nakłada spolszczenie Cairn (podmienia slot języka włoskiego). Wymaga Pythona z pakietami z requirements.txt.
set -e
GAME="${1:-H:/Gry/Steam/steamapps/common/Cairn}"
G="$GAME/Cairn_Data/StreamingAssets/aa/StandaloneWindows64"
HERE="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python}"
mkdir -p "$HERE/backup" "$HERE/build"
# Kopia zapasowa oryginałów (tylko jeśli jeszcze jej nie ma)
cp -n "$G/localizationit_assets_all.bundle" "$G/dynamicfontsit_assets_all.bundle" "$HERE/backup/"
"$PY" -X utf8 "$HERE/tools/patch_loc.py" "$G/localizationen_assets_all.bundle" "$HERE/backup/localizationit_assets_all.bundle" "$HERE/build/localizationit_assets_all.bundle"
"$PY" -X utf8 "$HERE/tools/patch_fonts.py" "$HERE/backup/dynamicfontsit_assets_all.bundle" "$HERE/build/dynamicfontsit_assets_all.bundle"
cp "$HERE/build/"*.bundle "$G/"
echo "Gotowe. W grze wybierz: Ustawienia -> Język -> Polski."
