import bpy,bmesh,math,sys,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import interpolate_bezier
from math import sin,cos,pi,exp
OUT=os.path.dirname(os.path.abspath(__file__));PART=os.environ.get('PART','all')
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;col=sc.collection
# ===== 1) user's head/face script, executed unmodified =====
exec(compile(open(os.path.join(OUT,'head_base_v2.py')).read(),'head_base_v2.py','exec'),{'__name__':'__main__'})
head=bpy.data.objects['V2_HEAD_Rounded_Chibi'];HC=Vector(head.location);bpy.context.view_layer.update()
HV=[head.matrix_world@v.co for v in head.data.vertices];bvh=BVHTree.FromPolygons(HV,[tuple(p.vertices) for p in head.data.polygons])
U=3.3
def SK(az,ph,off=0):
    d=Vector((sin(az)*sin(ph),-cos(az)*sin(ph),cos(ph)));hit=bvh.ray_cast(HC,d)[0];return hit+d*off*U
HEADONLY=PART=='head0'
# ===== 2) outfit: reuse the lofted/swept custom-mesh body, scaled under the head =====
src=open(os.path.join(OUT,'hero.py')).read();cut=lambda a,b:src[src.index(a):src.index(b)]
NS=dict(bpy=bpy,bmesh=bmesh,math=math,Vector=Vector,sin=sin,cos=cos,pi=pi,col=col,sc=sc,Q='draft')
exec(cut('# ---------------- materials','# ---------------- proportions'),NS)
SB=3.6;NK=1.23;BZ=NK-.48*SB
if PART=='all':
    before=set(bpy.data.objects);exec(cut('# ---------------- body','# ---------------- hair'),NS)
    for o in set(bpy.data.objects)-before:o.scale=(SB,SB,SB);o.location=(0,0,BZ)
TK=lambda x,y,z:Vector((x*3.1,y*3.1,NK+(z-.48)*SB))
# ===== 3) hair: Bezier centre lines cast onto the real head mesh, lens section, tapered, curled tips =====
mk=NS['mk'];M=NS['M'];M['hair']=NS['clay']('hair2','#e6cba2');M['hairb']=NS['clay']('hairb','#d6b98c')
def bez(K,res=12):
    K=[Vector(k) for k in K];n=len(K);T=[(K[min(n-1,i+1)]-K[max(0,i-1)])*(.5 if 0<i<n-1 else 1) for i in range(n)];P=[]
    for i in range(n-1):
        seg=interpolate_bezier(K[i],K[i]+T[i]/3,K[i+1]-T[i+1]/3,K[i+1],res+1);P+=seg[(1 if i else 0):]
    return P
def resample(P,N):
    L=[0]
    for i in range(1,len(P)):L.append(L[-1]+(P[i]-P[i-1]).length)
    out=[];j=0
    for k in range(N+1):
        s=L[-1]*k/N
        while j<len(P)-2 and L[j+1]<s:j+=1
        u=(s-L[j])/((L[j+1]-L[j]) or 1);out.append(P[j].lerp(P[j+1],u))
    return out
def frames(P,n0):
    N=len(P);T=[];Nn=[];n=Vector(n0)
    for i in range(N):
        tg=(P[min(N-1,i+1)]-P[max(0,i-1)]).normalized();n=n-tg*n.dot(tg);n=n.normalized() if n.length>1e-6 else tg.orthogonal().normalized();T.append(tg);Nn.append(n.copy())
    return T,Nn
ss=lambda x:max(0,min(1,x))**2*(3-2*max(0,min(1,x)))
STR={'fringe':[],'side':[],'back':[],'ahoge':[]}
def strand(grp,K,w0,th0,curl=None,groove=.0,N=34,flat=.5):
    w0*=U;th0*=U;P=resample(bez(K),N);T,Nn=frames(P,P[0]-HC+Vector((0,0,.2)))
    if curl:
        ang,ln,cd=curl;ln*=U;tg=T[-1];c=Vector(cd);c=(c-tg*c.dot(tg)).normalized();p=P[-1].copy();Mc=18
        for j in range(1,Mc+1):
            th=ang*(j/Mc)**.9;p=p+(tg*cos(th)+c*sin(th))*(ln/Mc*(1.5-j/Mc));P.append(p.copy())
        T,Nn=frames(P,Nn[0])
    L=[0]
    for i in range(1,len(P)):L.append(L[-1]+(P[i]-P[i-1]).length)
    A=[];B=[]
    for i in range(len(P)):
        t=L[i]/L[-1];rt=.5+.5*ss(t/.1);A.append(max(.004,w0*rt*(1-t**3.6)**.62));B.append(max(.004,th0*rt*(1-t**4)**.55))
    STR[grp].append(dict(P=P,T=T,N=Nn,A=A,B=B,g=groove,flat=flat))
def strand_mesh(s,seg=16):
    V=[];F=[];P=s['P'];n=len(P)
    for i in range(n):
        w=s['T'][i].cross(s['N'][i]).normalized()
        for j in range(seg):
            th=j/seg*2*pi;x=cos(th);y=sin(th);y=y*(1-s['g']*exp(-x*x*7)) if y>0 else y*s['flat'];V.append(P[i]+w*(x*s['A'][i])+s['N'][i]*(y*s['B'][i]))
        if i:
            for j in range(seg):F.append(((i-1)*seg+j,(i-1)*seg+(j+1)%seg,i*seg+(j+1)%seg,i*seg+j))
    V.append(P[0]-s['T'][0]*s['B'][0]*.6);V.append(P[-1]+s['T'][-1]*.006);c=len(V)-2
    for j in range(seg):F.append((c,(j+1)%seg,j));F.append((c+1,(n-1)*seg+j,(n-1)*seg+(j+1)%seg))
    return V,F
lerp=lambda a,b,t:a+(b-a)*t
def onskull(az0,az1,ph0,ph1,off,bulge=0,n=4,pw=1.4):
    return [SK(lerp(az0,az1,(k/n)**pw),lerp(ph0,ph1,k/n),off+bulge*sin(pi*k/n)) for k in range(n+1)]
# fringe: tips stop at the lash line above each eye, longer between and outside the eyes
for i,(a0,a1,ph,w,lay) in enumerate([(.0,.04,1.42,.03,1),(.2,.27,1.2,.046,0),(-.2,-.28,1.21,.046,0),(.42,.62,1.24,.05,1),(-.42,-.62,1.24,.05,1),(.7,1.0,1.62,.05,0),(-.7,-1.0,1.62,.05,0),(.1,.15,1.14,.03,1),(-.1,-.14,1.16,.03,1)]):
    sg=1 if a1>=a0 else -1;strand('fringe',onskull(a0,a1,.07,ph,.016+.014*lay,bulge=.014),w,.02,curl=(1.1,.045,(sg*cos(a1),sg*sin(a1),.0)),groove=.22 if w>.04 else 0)
for sg in (1,-1):
    strand('side',onskull(sg*.92,sg*1.12,.08,1.75,.024)+[TK(sg*.238,-.13,.56)],.036,.018,curl=(1.6,.05,(-sg,0,.1)))
    strand('side',onskull(sg*1.0,sg*1.15,.08,1.5,.034,bulge=.008)+[TK(sg*.262,-.125,.52),TK(sg*.232,-.15,.42),TK(sg*.268,-.132,.32),TK(sg*.24,-.142,.25)],.05,.022,curl=(2.7,.085,(sg,-.25,.3)),groove=.25)
    strand('side',onskull(sg*1.3,sg*1.45,.07,1.55,.024)+[TK(sg*.3,-.03,.52),TK(sg*.27,-.05,.4),TK(sg*.325,-.03,.3),TK(sg*.292,-.05,.21)],.074,.027,curl=(2.9,.1,(sg,-.15,.3)),groove=.28)
    strand('side',onskull(sg*1.65,sg*1.8,.08,1.6,.036,bulge=.006)+[TK(sg*.305,.075,.52),TK(sg*.28,.095,.4),TK(sg*.335,.085,.3),TK(sg*.31,.1,.2),TK(sg*.33,.1,.15)],.072,.027,curl=(2.7,.095,(sg,.2,.3)),groove=.25)
def backlock(az,ph0,off,zs,rho0,w,th,phase,amp,curl,groove):
    ax,ay=sin(az),-cos(az);tx,ty=cos(az),sin(az);K=onskull(az,az,ph0,1.72,off,pw=1);z0=zs[0];z1=zs[-1]
    for j,z in enumerate(zs):
        u=(z0-z)/(z0-z1+1e-6);rr=rho0+.06*u+.014*cos(phase+j*1.9);wv=amp*sin(phase+j*1.9)*(.4+.6*u);K.append(TK(ax*rr+tx*wv,.03+ay*rr*.92+ty*wv,z))
    sgn=1 if ax>.02 else (-1 if ax<-.02 else 1);strand('back',K,w,th,curl=(curl[0],curl[1],(ax*.5+sgn*abs(ay)*.9,ay*.5,.38)),groove=groove,N=40)
for i in range(9):
    az=pi+(i-4)*.33;L=.13+.05*((i*5)%3)/2;backlock(az,.3,.018,[.5,.42,.34,.26,L+.06],.25,.086,.03,i*.85,.03,(2.8,.1),.3)
for i in range(8):
    az=pi+(i-3.5)*.33;L=.34+.05*((i*7)%3)/2;backlock(az,.06,.042,[.5,.44,L+.04],.285,.076,.028,i*.85+1.4,.024,(2.6,.085),.25)
CR=SK(0,0.001)
strand('ahoge',[CR+Vector(k)*U for k in [(0,.012,-.02),(0,.04,.05),(0,.02,.11),(0,-.04,.135),(0,-.09,.11),(0,-.1,.075)]],.03,.03,flat=1,N=30)
for g in ([] if HEADONLY else STR):
    V=[];F=[]
    for s in STR[g]:
        v,f=strand_mesh(s);b=len(V);V+=v;F+=[tuple(i+b for i in q) for q in f]
    mk('HAIR_'+g,V,F,'hair',sub=1)
# scalp cap = the head's own surface pushed out (so hair sits on the real head shape)
keep=[];cv=[]
for v in HV:
    d=(v-HC).normalized();keep.append(d.z>.3 or (d.y>.05 and d.z>-.75));cv.append(v+d*.035*U*.3)
if not HEADONLY:mk('HAIR_cap',cv,[tuple(p.vertices) for p in head.data.polygons if all(keep[i] for i in p.vertices)],'hairb',sub=0)
# accessories from the earlier design, re-seated on the hair surface of this head
if PART=='all':
    az,el=.92,.5;d=Vector((sin(az)*cos(el),-cos(az)*cos(el),sin(el)));P=(bvh.ray_cast(HC,d)[0]+d*.2)/U;NS['ACC']=(P,d,Vector((cos(az),sin(az),0)),(Vector((0,0,1))-d*d.z).normalized())
    before=set(bpy.data.objects);exec(cut('# ---------------- flower','# ---------------- base').replace('P,d,r,u=hframe(.92,.5,1.2)','P,d,r,u=ACC'),NS)
    for o in set(bpy.data.objects)-before:o.scale=(U,U,U)
# ===== 4) stage =====
gz=BZ;bv=[];nb=56
for k in range(nb):a=k/nb*2*pi;bv+=[(cos(a)*1.8,sin(a)*1.8+.1,gz),(cos(a)*1.87,sin(a)*1.87+.1,gz-.16)]
if PART=='all':mk('base',bv,[tuple(range(0,2*nb,2))]+[(2*k,2*k+1,(2*k+3)%(2*nb),(2*k+2)%(2*nb)) for k in range(nb)],'grass',sub=0)
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.8,.79,.88,1);w.node_tree.nodes['Background'].inputs[1].default_value=.55
piv=bpy.data.objects.new('piv',None);col.objects.link(piv)
def light(loc,e,size,c=(1,1,1)):
    l=bpy.data.lights.new('l','AREA');l.energy=e*13;l.size=size*3.6;l.color=c;o=bpy.data.objects.new('L',l);col.objects.link(o);o.location=Vector(loc)*3.6;o.rotation_euler=(Vector((0,0,1.2))-o.location).to_track_quat('-Z','Y').to_euler();o.parent=piv
light((-2.0,-2.4,2.6),105,1.8,(1,.96,.9));light((2.4,-1.6,1.0),20,3,(.9,.93,1));light((.8,2.6,2.2),42,2)
cam=bpy.data.cameras.new('cam');cam.type='ORTHO';co=bpy.data.objects.new('cam',cam);col.objects.link(co);sc.camera=co
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=True;sc.view_settings.view_transform='Standard'
def shot(name,ang,elev,scale,tz,w,h):
    d=Vector((sin(ang)*cos(elev),-cos(ang)*cos(elev),sin(elev)));co.location=Vector((0,.1,tz))+d*20;co.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale;cam.clip_end=100;piv.rotation_euler=(0,0,ang)
    sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=os.path.join(OUT,'c_%s.png'%name);bpy.ops.render.render(write_still=True)
if PART=='head0':
    for n_,a in (('hfront',0),('hf34',-.6),('hside',pi/2)):shot(n_,a,.03,2.6,2.0,520,600)
else:
    mid=(gz+3.3)/2;S=5.4
    shot('hero',-.5,.14,S,mid,560,900);shot('front',0,.02,S,mid,306,441);shot('side',pi/2,.02,S,mid,306,441);shot('back',pi,.02,S,mid,300,441)
    shot('face',0,.02,2.5,2.0,306,441);shot('acc',.75,.1,2.9,2.2,306,441);shot('back34',pi-.6,.25,S,mid,300,441)
