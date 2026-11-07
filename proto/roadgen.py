# road network prototype on real island data. mode 'tile' = axis-aligned tiles only, 'free' = any angle (vector roads)
import json,sys,math,heapq
import numpy as np
from scipy import ndimage
from skimage.graph import MCP_Geometric
from PIL import Image,ImageDraw,ImageFont
FB='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc';FL='/usr/share/fonts/opentype/noto/NotoSansCJK-DemiLight.ttc'
seed=int(sys.argv[1]);mode=sys.argv[2];out=sys.argv[3]
d=json.load(open(f'isl_{seed}.json'));N=d['N'];t=np.array(d['t']).reshape(N,N);h=np.array(d['h']).reshape(N,N).astype(float)
land=t==0;ocean=t==2;river=t==1;rng=np.random.default_rng(seed)
hs=ndimage.gaussian_filter(h,1.2);gy,gx=np.gradient(hs);slope=np.hypot(gx,gy)
cdist=ndimage.distance_transform_edt(~ocean);rdist=ndimage.distance_transform_edt(~river)
flat=land&(slope<.35)&(h<=np.percentile(h[land],70))
# ---------- centres
fa=ndimage.uniform_filter(flat.astype(float),25)
def pick(score,mask):
    s=np.where(mask,score,-1e9);i=int(np.argmax(s));return (i//N,i%N)
ys,xs=np.mgrid[0:N,0:N]
dt=pick(fa*100-np.minimum(rdist,30)*1.5-np.abs(cdist-25)*.4,flat&(cdist>10))
C=[dt];
for k in range(4):
    dmin=np.min([np.hypot(ys-c[0],xs-c[1]) for c in C],axis=0)
    sc=fa*100-np.abs(dmin-38)*2.5+rng.random((N,N))*4
    c=pick(sc,flat&(dmin>28)&(cdist>6))
    if fa[c]>.45:C.append(c)
# coastal / rural villages
V=[]
for k in range(7):
    dmin=np.min([np.hypot(ys-c[0],xs-c[1]) for c in C+V],axis=0)
    c=pick(-np.abs(cdist-4)*3+np.minimum(dmin,60)+rng.random((N,N))*6,land&(cdist>2)&(cdist<9)&(slope<.5)&(dmin>30))
    if dmin[c]>30:V.append(c)
# ---------- cost
base=1+slope*14+np.maximum(0,h-np.percentile(h[land],60))*.15
base[river]=12;base[ocean]=np.inf
roads=np.zeros((N,N),np.uint8)   # 0 none 1 local 2 collector 3 arterial 4 highway
def path_free(a,b,cost):
    m=MCP_Geometric(cost,fully_connected=True);m.find_costs([a],[b]);return m.traceback(b)
def path_tile(a,b,cost,turn=6.):
    # dijkstra on (y,x,dir) with turn penalty -> long straight-ish segments that still follow terrain
    D=np.full((N,N,4),np.inf);P={};DIR=[(0,1),(1,0),(0,-1),(-1,0)];pq=[]
    for k in range(4):D[a[0],a[1],k]=0;heapq.heappush(pq,(0,a[0],a[1],k))
    while pq:
        dd,y,x,k=heapq.heappop(pq)
        if dd>D[y,x,k]:continue
        if (y,x)==b:
            seq=[(y,x)];s=(y,x,k)
            while s in P:s=P[s];seq.append((s[0],s[1]))
            return seq[::-1]
        for k2,(dy,dx) in enumerate(DIR):
            if (k2+2)%4==k:continue
            yy,xx=y+dy,x+dx
            if not(0<=yy<N and 0<=xx<N):continue
            c=cost[yy,xx]
            if not np.isfinite(c):continue
            nd=dd+c+(turn if k2!=k else 0)
            if nd<D[yy,xx,k2]:D[yy,xx,k2]=nd;P[(yy,xx,k2)]=(y,x,k);heapq.heappush(pq,(nd,yy,xx,k2))
    return []
PATH=path_tile if mode=='tile' else path_free
def smooth(p,it=4):
    q=[(float(y),float(x)) for y,x in p]
    for _ in range(it):
        r=[q[0]]
        for i in range(len(q)-1):a,b=q[i],q[i+1];r+=[(a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25),(a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75)]
        r.append(q[-1]);q=r
    return q
segs=[]  # (level, list of points) for rendering
def add(a,b,lev,reuse=.35):
    cost=base.copy();cost[roads>=2]*=reuse
    p=PATH(a,b,cost)
    if not p:return
    if mode=='free':p=smooth(p)
    for (y,x) in p:roads[int(round(y)),int(round(x))]=max(roads[int(round(y)),int(round(x))],lev)
    segs.append((lev,p))
# radial arterials from downtown to sub-centres, then villages to nearest network
for c in C[1:]:add(dt,c,3)
for v in V:
    net=np.argwhere(roads>=2);j=np.argmin(np.hypot(net[:,0]-v[0],net[:,1]-v[1]));add(tuple(net[j]),v,3)
# ring road around downtown through 10 waypoints
R=np.median([math.hypot(c[0]-dt[0],c[1]-dt[1]) for c in C[1:]])*.55 if len(C)>1 else 30
wp=[]
for k in range(10):
    a=k/10*2*math.pi;best=None
    for rr in np.linspace(R*.8,R*1.25,8):
        y,x=int(dt[0]+math.sin(a)*rr),int(dt[1]+math.cos(a)*rr)
        if 0<=y<N and 0<=x<N and land[y,x] and (best is None or base[y,x]<base[best]):best=(y,x)
    if best:wp.append(best)
for k in range(len(wp)):add(wp[k],wp[(k+1)%len(wp)],4,reuse=.6)
# riverside road inside urban radius
urb=np.min([np.hypot(ys-c[0],xs-c[1])/(30 if i else 40) for i,c in enumerate(C)],axis=0)<1
band=land&(np.abs(rdist-2.5)<.8)&urb
lab,n=ndimage.label(band)
for k in range(1,n+1):
    pts=np.argwhere(lab==k)
    if len(pts)<25:continue
    # endpoints = farthest pair
    i=np.argmax(np.hypot(pts[:,0]-pts[0,0],pts[:,1]-pts[0,1]));j=np.argmax(np.hypot(pts[:,0]-pts[i,0],pts[:,1]-pts[i,1]))
    cost=np.where(band,1.,40.);cost[ocean]=np.inf;p=PATH(tuple(pts[i]),tuple(pts[j]),cost)
    if mode=='free':p=smooth(p)
    for (y,x) in p:roads[int(round(y)),int(round(x))]=max(roads[int(round(y)),int(round(x))],2)
    segs.append((2,p))
# ---------- local streets
# orientation field: angle of nearest major road tangent
maj=roads>=2
tang=np.full((N,N),np.nan)
for lev,p in segs:
    for q in range(len(p)):
        a=p[max(0,q-4)];b=p[min(len(p)-1,q+4)];tang[int(round(p[q][0])),int(round(p[q][1]))]=math.atan2(b[0]-a[0],b[1]-a[1])
_,(iy,ix)=ndimage.distance_transform_edt(np.isnan(tang),return_indices=True)
field=tang[iy,ix]
loc=[]
def blocked(y,x):return not(0<=y<N and 0<=x<N) or not land[int(y),int(x)] or not urb[int(y),int(x)]
occ=np.zeros((N,N),bool);occ|=maj
def trace(y,x,ang0,sep):
    pts=[(y,x)];a=ang0
    for st in range(140):
        f=field[int(y),int(x)];cands=[f,f+math.pi/2,f+math.pi,f-math.pi/2];a=min(cands,key=lambda c:abs(math.atan2(math.sin(c-a),math.cos(c-a))))
        y2,x2=y+math.sin(a),x+math.cos(a)
        if blocked(y2,x2):break
        y,x=y2,x2;pts.append((y,x))
        if st>2 and maj[int(y),int(x)]:break
        if st>3 and occ[int(y),int(x)]:break
    return pts
dist_occ=None
cand=np.argwhere(urb&land&~maj);rng.shuffle(cand)
for it,(y,x) in enumerate(cand[:9000]):
    if it%40==0:dist_occ=ndimage.distance_transform_edt(~occ)
    if dist_occ[y,x]<4.5:continue
    sep=5;f=field[y,x]
    for a in (f,f+math.pi/2):
        for s in (0,math.pi):
            p=trace(y+.5,x+.5,a+s,sep)
            if len(p)>4:
                loc.append(p)
                for (py,px) in p:occ[int(py),int(px)]=True
# tile mode: snap local streets to axis-aligned staircase-free form (keep only dominant-axis runs)
# ---------- render
S=4;W=N*S;img=Image.new('RGB',(W,W));px=np.zeros((N,N,3))
px[ocean]=(46,98,150);px[river]=(70,140,190);px[land]=(150,178,110)
sh=np.clip(1+(-gx-gy)*.25,.7,1.3)[...,None];px=np.where(land[...,None],np.clip(px*sh,0,255),px)
px[land&urb]=px[land&urb]*.7+np.array([214,206,190])*.3
img=Image.fromarray(px.astype(np.uint8)).resize((W,W),Image.BICUBIC);dr=ImageDraw.Draw(img,'RGBA')
def poly(p,w,c):
    q=[(x*S+S/2,y*S+S/2) for (y,x) in p]
    if mode=='tile':
        for (y,x) in p:dr.rectangle((x*S-(w-S)/2,y*S-(w-S)/2,x*S+S+(w-S)/2,y*S+S+(w-S)/2),fill=c)
    else:dr.line(q,fill=c,width=int(w),joint='curve')
for p in loc:
    if mode=='tile':
        q=[(int(y),int(x)) for (y,x) in p];
        for (y,x) in q:dr.rectangle((x*S,y*S,x*S+S,y*S+S),fill=(110,110,116))
    else:poly(p,2,(105,105,112))
for lev,p in sorted(segs,key=lambda s:s[0]):
    poly(p,{2:4,3:6,4:7}[lev],{2:(70,72,80),3:(40,40,46),4:(240,200,90)}[lev])
fb=ImageFont.truetype(FB,30);fl=ImageFont.truetype(FL,20)
for i,c in enumerate(C):dr.ellipse((c[1]*S-8,c[0]*S-8,c[1]*S+8,c[0]*S+8),fill=(40,90,200) if i==0 else (236,150,70),outline=(255,255,255),width=3)
for v in V:dr.ellipse((v[1]*S-6,v[0]*S-6,v[1]*S+6,v[0]*S+6),fill=(120,170,60),outline=(255,255,255),width=2)
ttl={'tile':'시안 A · 타일 도로 (가로·세로만)','free':'시안 B · 자유 각도 도로'}[mode]
dr.rounded_rectangle((20,20,20+620,20+60),radius=12,fill=(18,22,30,220));dr.text((36,26),ttl,font=fb,fill=(255,255,255))
lg=[((240,200,90),'순환도로'),((40,40,46),'방사 간선'),((70,72,80),'강변로'),((105,105,112),'생활도로')]
y0=W-60;x0=24
dr.rounded_rectangle((16,y0-10,16+560,y0+44),radius=10,fill=(18,22,30,210))
for c,tx in lg:dr.rectangle((x0,y0+10,x0+28,y0+18),fill=c);dr.text((x0+34,y0+2),tx,font=fl,fill=(255,255,255));x0+=136
img.save(out)
print('ok',len(C),len(V),len(loc))
