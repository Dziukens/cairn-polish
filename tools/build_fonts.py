import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sdflib import *
from synth import mark_mask, composite
from atlas import pack, PAD, SPREAD
import freetype, pickle, lzma
PL="ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
BASE={'ą':'a','ć':'c','ę':'e','ł':'l','ń':'n','ó':'o','ś':'s','ź':'z','ż':'z','Ą':'A','Ć':'C','Ę':'E','Ł':'L','Ń':'N','Ó':'O','Ś':'S','Ź':'Z','Ż':'Z'}
ANCH={'ł':'center','Ł':'left'}
COPY_DE="„‚"  # copy from German supplement atlas
# (IT asset name, EN asset name, DE asset name, ttf or None)
ASSETS=[('Cairn_TextFont IT','Cairn_TextFont','Cairn_TextFont DE',None),
        ('IT Boxed-RegularItalic SDF','Boxed-RegularItalic SDF','DE Boxed-RegularItalic SDF','Boxed-RegularItalic'),
        ('IT Boxed-DemiBold SDF','Boxed-DemiBold SDF','DE Boxed-DemiBold SDF','Boxed-DemiBold'),
        ('IT Boxed-DemiBoldItalic SDF','Boxed-DemiBoldItalic SDF','DE Boxed-DemiBoldItalic SDF','Boxed-DemiBoldItalic'),
        ('IT Boxed-Bold SDF','Boxed-Bold SDF','DE Boxed-Bold SDF','Boxed-Bold')]
def ttf_glyph(ttf,ch):
    bits,l,t,adv=render_mask_x(ttf,ch)
    d,box=sdf_from_mask(bits,l,t,PAD,SPREAD)
    face=freetype.Face(ttf); face.set_char_size(250*64,0,72,72)
    face.load_char(ch, freetype.FT_LOAD_NO_HINTING|freetype.FT_LOAD_NO_SCALE)
    # metrics in px: use hi-res bbox
    ys,xs=np.nonzero(bits)
    left=(l+xs.min())/SS; right=(l+xs.max()+1)/SS; top=(t-ys.min())/SS; bot=(t-ys.max()-1)/SS
    # use exact outline metrics from freetype unscaled for precision
    face.set_char_size(250*64,0,72,72); face.load_char(ch, freetype.FT_LOAD_NO_HINTING)
    m=face.glyph.metrics
    met={'m_Width':m.width/64,'m_Height':m.height/64,'m_HorizontalBearingX':m.horiBearingX/64,'m_HorizontalBearingY':m.horiBearingY/64,'m_HorizontalAdvance':m.horiAdvance/64}
    return encode(d,SPREAD),box,met,face.get_char_index(ord(ch))
def build():
    out={}
    for it_name,en_name,de_name,ttfname in ASSETS:
        IT=Atlas(f'fontsx/it_{it_name}.json',f'fontsx/it_{it_name} Atlas.png')
        EN=Atlas(f'fontsx/en_{en_name}.json',f'fontsx/en_{en_name} Atlas.png')
        DE=Atlas(f'fontsx/de_{de_name}.json',f'fontsx/de_{de_name} Atlas.png')
        glyphs=[]  # (char, sdf array top-first incl pad, metrics, glyph index)
        for c in IT.A['m_CharacterTable']:
            ch=chr(c['m_Unicode']); a,box,m=IT.glyph(ch); glyphs.append((ch,a,m,c['m_GlyphIndex']))
        for ch in COPY_DE:
            a,box,m=DE.glyph(ch); glyphs.append((ch,a,m,DE.c[ord(ch)]['m_GlyphIndex']))
        for ch in PL:
            if ttfname:
                a,box,met,gi=ttf_glyph(f'fontsx/{ttfname}.ttf',ch)
            else:
                b=BASE[ch]
                mk,lp,tp,rb=mark_mask('fontsx/Boxed-RegularItalic.ttf',ch,b,unslant=9)
                a,box,met=composite(EN,b,mk,lp,tp,rb,anchor=ANCH.get(ch,'scale'))
                face=freetype.Face('fontsx/Boxed-RegularItalic.ttf'); gi=face.get_char_index(ord(ch))
                met={k:float(v) for k,v in met.items()}
            glyphs.append((ch,a,met,gi))
        out[it_name]=glyphs
    return out
if __name__=='__main__':
    res=build()
    q={n:[(ch,(np.clip(a,0,1)*255+0.5).astype(np.uint8),m,gi) for ch,a,m,gi in g] for n,g in res.items()}
    with lzma.open('pl_glyphs.pkl.xz','wb') as f: pickle.dump(q,f,protocol=4)
    for k,g in res.items():
        pos,H=pack(g); print(k,len(g),'atlas 1024x',H)
