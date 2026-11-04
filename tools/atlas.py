"""Atlas constants and glyph packing shared by build_fonts.py and patch_fonts.py."""
SPREAD=26; PAD=25
def pack(glyphs, W=1024):
    x=1;y=1;rowh=0;pos=[]
    for ch,a,m,gi in glyphs:
        h,w=a.shape
        if x+w+1>W: x=1;y+=rowh+1;rowh=0
        pos.append((x,y)); x+=w+1; rowh=max(rowh,h)
    H=y+rowh+1
    Hp=1
    while Hp<H: Hp*=2
    return pos,Hp
