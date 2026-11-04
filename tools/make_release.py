"""Packs build/*.bundle and release/CZYTAJ.txt into dist/Cairn-PL-<version>.zip (extract into the game folder)."""
import sys, os, zipfile
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
ver=sys.argv[1]
GAME_DIR="Cairn_Data/StreamingAssets/aa/StandaloneWindows64/"
os.makedirs(os.path.join(ROOT,"dist"), exist_ok=True)
out=os.path.join(ROOT,"dist",f"Cairn-PL-{ver}.zip")
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in ("localizationit_assets_all.bundle","dynamicfontsit_assets_all.bundle"):
        z.write(os.path.join(ROOT,"build",name), GAME_DIR+name)
    readme=open(os.path.join(ROOT,"release","CZYTAJ.txt"),encoding="utf-8").read()
    z.writestr("CZYTAJ.txt", "﻿"+readme.replace("\n","\r\n"))
print(out, os.path.getsize(out))
