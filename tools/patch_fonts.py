"""Writes Polish glyph supplements into the Italian font bundle."""
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import UnityPy, pickle, lzma, numpy as np
from PIL import Image
from build_fonts import pack, PAD
from UnityPy.enums import TextureFormat
src, dst = sys.argv[1], sys.argv[2]
# glyph SDFs stored as uint8 (the atlas is Alpha8, so this is lossless)
with lzma.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pl_glyphs.pkl.xz'),'rb') as f:
    res={n:[(ch,a.astype(np.float32)/255,m,gi) for ch,a,m,gi in gl] for n,gl in pickle.load(f).items()}
env=UnityPy.load(src)
objs={o.path_id:o for o in env.objects}
texinfo={}  # tex path_id -> (W,H)
for o in env.objects:
    if o.type.name!="MonoBehaviour": continue
    t=o.read_typetree()
    if t.get('m_Name') not in res: continue
    glyphs=res[t['m_Name']]
    W=1024; pos,H=pack(glyphs,W)
    atlas=np.zeros((H,W),np.float32)  # bottom-left origin
    gt=[];ct=[];used=[]
    for (ch,a,m,gi),(x,y) in zip(glyphs,pos):
        h,w=a.shape
        atlas[y:y+h, x:x+w]=np.maximum(atlas[y:y+h, x:x+w], a[::-1])
        rect={'m_X':x+PAD,'m_Y':y+PAD,'m_Width':w-2*PAD,'m_Height':h-2*PAD}
        gt.append({'m_Index':int(gi),'m_Metrics':{k:float(v) for k,v in m.items()},'m_GlyphRect':rect,'m_Scale':1.0,'m_AtlasIndex':0,'m_ClassDefinitionType':0})
        ct.append({'m_ElementType':1,'m_Unicode':ord(ch),'m_GlyphIndex':int(gi),'m_Scale':1.0})
        used.append({'m_X':x,'m_Y':y,'m_Width':w,'m_Height':h})
    # sanity: unique glyph indices
    assert len({g['m_Index'] for g in gt})==len(gt), t['m_Name']
    # keep element layout of existing char entries
    tmpl=t['m_CharacterTable'][0]
    ct=[{**tmpl, **c} for c in ct]
    t['m_GlyphTable']=gt; t['m_CharacterTable']=ct
    t['m_UsedGlyphRects']=used; t['m_FreeGlyphRects']=[]
    t['m_AtlasWidth']=W; t['m_AtlasHeight']=H
    o.save_typetree(t)
    tex_id=t['m_AtlasTextures'][0]['m_PathID']
    tex=objs[tex_id].read()
    img=Image.fromarray((np.clip(atlas,0,1)[::-1]*255+0.5).astype(np.uint8),'L').convert('RGBA')
    img.putalpha(Image.fromarray((np.clip(atlas,0,1)[::-1]*255+0.5).astype(np.uint8),'L'))
    tex.set_image(img, target_format=TextureFormat.Alpha8, mipmap_count=1)
    tex.save()
    texinfo[tex_id]=(W,H)
    print('font',t['m_Name'],len(gt),'glyphs ->',W,'x',H)
for o in env.objects:
    if o.type.name!="Material": continue
    t=o.read_typetree(); sp=t['m_SavedProperties']
    mt=[v for k,v in sp['m_TexEnvs'] if k=='_MainTex']
    if not mt or mt[0]['m_Texture']['m_PathID'] not in texinfo: continue
    W,H=texinfo[mt[0]['m_Texture']['m_PathID']]
    sp['m_Floats']=[[k,(float(W) if k=='_TextureWidth' else float(H) if k=='_TextureHeight' else v)] for k,v in sp['m_Floats']]
    o.save_typetree(t); print('material',t['m_Name'],W,H)
open(dst,'wb').write(env.file.save(packer="lz4"))
print('saved',dst,os.path.getsize(dst))
