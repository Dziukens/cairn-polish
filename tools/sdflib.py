import freetype, numpy as np, json
from scipy.ndimage import distance_transform_edt
from PIL import Image
SS=8  # supersampling
def render_mask(ttf, ch, pt=250, ss=SS):
    """Return (mask hi-res bool array, left, top) in hi-res pixel units; origin baseline. top = y of first row (font up)."""
    face=freetype.Face(ttf); face.set_char_size(int(pt*ss*64),0,72,72)
    face.load_char(ch, freetype.FT_LOAD_RENDER|freetype.FT_LOAD_TARGET_MONO|freetype.FT_LOAD_NO_HINTING)
    bm=face.glyph.bitmap; w,h,p=bm.width,bm.rows,bm.pitch
    buf=np.frombuffer(bytes(bm.buffer),dtype=np.uint8).reshape(h,p) if h else np.zeros((0,p),np.uint8)
    bits=np.unpackbits(buf,axis=1)[:,:w].astype(bool)
    adv=face.glyph.advance.x/64/ss
    return bits, face.glyph.bitmap_left, face.glyph.bitmap_top, adv
def sdf_from_mask(bits, left, top, pad, spread, ss=SS, box=None):
    """bits hi-res; returns (sdf float array top-row-first, box=(x0,y0top,w,h) in target px)."""
    if box is None:
        x0=np.floor(left/ss); x1=np.ceil((left+bits.shape[1])/ss)
        yt=np.ceil(top/ss); yb=np.floor((top-bits.shape[0])/ss)
        box=(int(x0),int(yt),int(x1-x0),int(yt-yb))
    x0,yt,w,h=box
    W=(w+2*pad)*ss; H=(h+2*pad)*ss
    canvas=np.zeros((H,W),bool)
    ox=left-(x0-pad)*ss; oy=(yt+pad)*ss-top
    canvas[oy:oy+bits.shape[0], ox:ox+bits.shape[1]]=bits
    din=distance_transform_edt(canvas); dout=distance_transform_edt(~canvas)
    d=(din-dout)/ss  # positive inside, in target px
    # downsample by averaging
    d=d.reshape(H//ss,ss,W//ss,ss).mean(axis=(1,3))
    return d, box
def encode(d, spread):
    return np.clip(0.5+d/(2*spread),0,1)

import math
from scipy.ndimage import binary_dilation, shift as ndshift
def render_mask_x(ttf, ch, pt=250, ss=SS, unslant=0.0):
    face=freetype.Face(ttf); face.set_char_size(int(pt*ss*64),0,72,72)
    if unslant:
        t=math.tan(math.radians(unslant))
        m=freetype.Matrix(int(65536),int(-t*65536),0,int(65536))  # x' = x - t*y
        face.set_transform(m, freetype.Vector(0,0))
    face.load_char(ch, freetype.FT_LOAD_RENDER|freetype.FT_LOAD_TARGET_MONO|freetype.FT_LOAD_NO_HINTING)
    bm=face.glyph.bitmap; w,h,p=bm.width,bm.rows,bm.pitch
    buf=np.frombuffer(bytes(bm.buffer),dtype=np.uint8).reshape(h,p) if h else np.zeros((0,p),np.uint8)
    bits=np.unpackbits(buf,axis=1)[:,:w].astype(bool) if h else np.zeros((0,w),bool)
    return bits, face.glyph.bitmap_left, face.glyph.bitmap_top, face.glyph.advance.x/64/ss

class Atlas:
    """Existing TMP font asset json + atlas (bottom-left origin array of floats)."""
    def __init__(self, jpath, pngpath):
        self.A=json.load(open(jpath)); self.pad=self.A['m_AtlasPadding']
        self.img=np.asarray(Image.open(pngpath).convert('RGBA'))[:,:,3].astype(float)[::-1]/255
        self.g={x['m_Index']:x for x in self.A['m_GlyphTable']}
        self.c={x['m_Unicode']:x for x in self.A['m_CharacterTable']}
    def has(self,ch): return ord(ch) in self.c
    def glyph(self,ch):
        """returns (sdf-encoded array top-first incl padding, box(x0,ytop,w,h), metrics)"""
        gl=self.g[self.c[ord(ch)]['m_GlyphIndex']]; r=gl['m_GlyphRect']; m=gl['m_Metrics']; p=self.pad
        a=self.img[r['m_Y']-p:r['m_Y']+r['m_Height']+p, r['m_X']-p:r['m_X']+r['m_Width']+p][::-1].copy()
        x0=math.floor(m['m_HorizontalBearingX']); yt=math.ceil(m['m_HorizontalBearingY'])
        return a,(x0,yt,r['m_Width'],r['m_Height']),dict(m)
