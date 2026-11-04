"""Builds the Polish string table into the Italian localization bundle (falls back to English)."""
import sys, os, re, glob, UnityPy
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","translation")
EN_BUNDLE, IT_BUNDLE, DST = sys.argv[1], (sys.argv[2] if len(sys.argv)>2 else None), (sys.argv[3] if len(sys.argv)>3 else None)
en=UnityPy.load(EN_BUNDLE); en_t=[o for o in en.objects if o.type.name=="MonoBehaviour"][0].read_typetree()
# unique EN texts in order of first appearance; @@N in pl/*.txt indexes this list
order=list(dict.fromkeys(k['text'] for g in en_t['texts'] for k in g['keys']))
ALLOWED=set(r' !"#%&\'()*+,-./0123456789:;<=>?ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]_abcdefghijklmnopqrstuvwxyz{}©àçèéû–—’“”…™'
            '°ÈÌìòù„‚ąćęłńóśźżĄĆĘŁŃÓŚŹŻ\n\t')
TAG=re.compile(r'<[^>]+>|\{[^}]*\}')
def parse(path):
    out={}; cur=None; buf=[]
    for line in open(path,encoding='utf-8').read().split('\n'):
        m=re.fullmatch(r'@@(\d+)',line)
        if m:
            if cur is not None: out[cur]='\n'.join(buf)
            cur=int(m.group(1)); buf=[]
        else: buf.append(line)
    if cur is not None: out[cur]='\n'.join(buf)
    return {k:(v[:-1] if v.endswith('\n') else v) for k,v in out.items()}
pl={}; problems=0
for f in sorted(glob.glob(P+"/pl/*.txt")):
    for i,t in parse(f).items():
        src=order[i]
        if sorted(TAG.findall(src))!=sorted(TAG.findall(t)):
            print(f"[TAG] {os.path.basename(f)} @@{i}: {TAG.findall(src)} vs {TAG.findall(t)}"); problems+=1
        bad={c for c in t if c not in ALLOWED and c not in src}
        if bad: print(f"[CHAR] {os.path.basename(f)} @@{i}: {''.join(sorted(bad))!r}"); problems+=1
        pl[src]=t
print(f"translated {len(pl)}/{len(order)} unique texts, problems: {problems}")
if not DST: sys.exit(0)
it=UnityPy.load(IT_BUNDLE); it_o=[o for o in it.objects if o.type.name=="MonoBehaviour"][0]; it_t=it_o.read_typetree()
assert [g['flags'] for g in en_t['texts']]==[g['flags'] for g in it_t['texts']]
for g_en,g_it in zip(en_t['texts'],it_t['texts']):
    g_it['keys']=[{'id':k['id'],'text':pl.get(k['text'],k['text'])} for k in g_en['keys']]
LANG_SELF,LANG_IT=-284612933,1903631653
for g in it_t['texts']:
    for k in g['keys']:
        if k['id']['value'] in (LANG_SELF,LANG_IT): k['text']='Polski'
it_o.save_typetree(it_t)
open(DST,'wb').write(it.file.save(packer="lz4"))
print('saved',DST,os.path.getsize(DST))
