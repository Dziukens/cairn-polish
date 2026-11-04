#!/usr/bin/env bash
# Przywraca oryginalne (włoskie) pliki gry z kopii zapasowej.
GAME="${1:-H:/Gry/Steam/steamapps/common/Cairn}"
cp "$(cd "$(dirname "$0")" && pwd)/backup/"*.bundle "$GAME/Cairn_Data/StreamingAssets/aa/StandaloneWindows64/" && echo "Przywrócono oryginał."
