import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from sdflib import *
from atlas import PAD, SPREAD
def mask_to_world(bits,l,t,ss=SS):
    """return list of hi-res coordinates helper: bbox in target px (x0,x1,ytop,ybot)"""
    return (l/ss,(l+bits.shape[1])/ss,t/ss,(t-bits.shape[0])/ss)
def bbox_of(bits,l,t,ss=SS):
    ys,xs=np.nonzero(bits)
    return (l+xs.min())/ss,(l+xs.max()+1)/ss,(t-ys.min())/ss,(t-ys.max()-1)/ss
def mark_mask(ref_ttf, P, Bch, unslant=0, grow=2):
    bp,lp,tp,_=render_mask_x(ref_ttf,P,unslant=unslant)
    bb,lb,tb,_=render_mask_x(ref_ttf,Bch,unslant=unslant)
    # place B mask in P's frame
    canvas=np.zeros_like(bp)
    dx=lb-lp; dy=tp-tb
    H,W=bb.shape
    ys0=max(0,dy); xs0=max(0,dx)
    sub=bb[max(0,-dy):, max(0,-dx):]
    h=min(sub.shape[0],canvas.shape[0]-ys0); w=min(sub.shape[1],canvas.shape[1]-xs0)
    canvas[ys0:ys0+h, xs0:xs0+w]=sub[:h,:w]
    canvas=binary_dilation(canvas,iterations=grow)
    mk=bp & ~canvas
    # remove tiny specks
    from scipy.ndimage import label
    lab,n=label(mk); 
    if n>1:
        sizes=np.bincount(lab.ravel()); keep=[i for i in range(1,n+1) if sizes[i]>200]
        mk=np.isin(lab,keep)
    return mk,lp,tp,bbox_of(bb,lb,tb)
def composite(target:Atlas, Bch, mk, lp, tp, refB_bbox, anchor='center', erode=0.0, extra_dx=0):
    base,box,m=target.glyph(Bch)
    # target base bbox in px from metrics
    tl=m['m_HorizontalBearingX']; tr=tl+m['m_Width']
    rl,rr=refB_bbox[0],refB_bbox[1]
    # mark bbox
    mb=bbox_of(mk,lp,tp)
    mcx=(mb[0]+mb[1])/2
    if anchor=='center': nx=(mcx-(rl+rr)/2)+(tl+tr)/2
    elif anchor=='right': nx=mcx-rr+tr
    elif anchor=='left': nx=mcx-rl+tl
    elif anchor=='scale': nx=tl+(mcx-rl)*(tr-tl)/(rr-rl)
    shiftx=nx-mcx+extra_dx
    # new glyph box = union
    lp2=lp+shiftx*SS
    mx0=math.floor(min(mb[0]+shiftx,tl)); mx1=math.ceil(max(mb[1]+shiftx,tr))
    yt=math.ceil(max(mb[2],m['m_HorizontalBearingY'])); yb=math.floor(min(mb[3],m['m_HorizontalBearingY']-m['m_Height']))
    nbox=(mx0,yt,mx1-mx0,yt-yb)
    d,_=sdf_from_mask(mk,int(round(lp2)),tp,PAD,SPREAD,box=nbox)
    md=encode(d-erode,SPREAD)
    # place base into new box
    out=np.zeros((nbox[3]+2*PAD,nbox[2]+2*PAD))
    ox=box[0]-nbox[0]; oy=nbox[1]-box[1]
    out[oy:oy+base.shape[0], ox:ox+base.shape[1]]=base
    out=np.maximum(out,md)
    # metrics
    top=max(mb[2],m['m_HorizontalBearingY']); bot=min(mb[3],m['m_HorizontalBearingY']-m['m_Height'])
    left=min(mb[0]+shiftx,tl); right=max(mb[1]+shiftx,tr)
    met={'m_Width':right-left,'m_Height':top-bot,'m_HorizontalBearingX':left,'m_HorizontalBearingY':top,'m_HorizontalAdvance':m['m_HorizontalAdvance']}
    return out,nbox,met
if __name__=='__main__':
    R=Atlas('fontsx/en_Cairn_TextFont.json','fontsx/en_Cairn_TextFont Atlas.png')
    for P,Bc,anc in [('é','e','center'),('ç','c','center'),('è','e','center'),('à','a','center'),('û','u','center')]:
        gt,gbox,gm=R.glyph(P)
        for name,ttf,uns,er in [('DB','fontsx/Boxed-DemiBold.ttf',0,0),('DBer','fontsx/Boxed-DemiBold.ttf',0,2.5),('RI','fontsx/Boxed-RegularItalic.ttf',9,0)]:
            mk,lp,tp,rb=mark_mask(ttf,P,Bc,unslant=uns)
            out,nbox,met=composite(R,Bc,mk,lp,tp,rb,anchor=anc,erode=er)
            # compare in common frame
            H=max(gbox[1],nbox[1])-min(gbox[1]-gbox[3],nbox[1]-nbox[3])+2*PAD; X0=min(gbox[0],nbox[0]); W=max(gbox[0]+gbox[2],nbox[0]+nbox[2])-X0+2*PAD; YT=max(gbox[1],nbox[1])
            A=np.zeros((H,W));Bm=np.zeros((H,W))
            A[YT-gbox[1]:YT-gbox[1]+gt.shape[0], gbox[0]-X0:gbox[0]-X0+gt.shape[1]]=gt
            Bm[YT-nbox[1]:YT-nbox[1]+out.shape[0], nbox[0]-X0:nbox[0]-X0+out.shape[1]]=out
            err=np.abs(A-Bm).mean(); iou=((A>.5)&(Bm>.5)).sum()/((A>.5)|(Bm>.5)).sum()
            print(P,name,'err %.4f IoU %.3f'%(err,iou),'met',{k:round(v,2) for k,v in met.items()},'gt',gm)
            Image.fromarray((np.hstack([A,Bm,np.abs(A-Bm)])*255).astype(np.uint8)).save(f'cmp_{ord(P)}_{name}.png')
