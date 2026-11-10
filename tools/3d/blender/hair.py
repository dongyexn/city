import bpy,math,sys,os
import numpy as np
from mathutils import Vector
from mathutils.geometry import interpolate_bezier
from math import sin,cos,pi,exp
OUT=os.path.dirname(os.path.abspath(__file__));MODE=sys.argv[-1] if sys.argv[-1] in('curve','sdf') else 'curve'
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;col=sc.collection
def clay(name,rgb,gloss=False,bump=.1):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;b=nt.nodes.get('Principled BSDF');c=[((int(rgb[i:i+2],16)/255)**2.2) for i in (1,3,5)]+[1]
    def S(k,v):
        i=b.inputs.get(k)
        if i is not None:i.default_value=v
    S('Base Color',c);S('Roughness',.18 if gloss else .85);S('Subsurface Weight',0 if gloss else .1);S('Subsurface Radius',(.08,.05,.04));S('Subsurface Scale',.04);S('Sheen Weight',0 if gloss else .25);S('Coat Weight',.5 if gloss else 0)
    if not gloss:
        n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=60;n.inputs['Detail'].default_value=6;bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=bump;bp.inputs['Distance'].default_value=.004;nt.links.new(n.outputs[0],bp.inputs['Height']);nt.links.new(bp.outputs[0],b.inputs['Normal'])
    return m
M={k:clay(k,v) for k,v in dict(skin='#ffe9da',hair='#e6cba2',hairb='#d6b98c',pink='#ffaaa6',mouth='#c47a70',stand='#c9c6d6').items()}
for k,v in dict(ink='#352d4a',eye='#5f4aa0',pupil='#43306e',hl='#ffffff').items():M[k]=clay(k,v,gloss=True)
def mk(name,V,F,mat,sub=0):
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in V],[],F);me.update();me.polygons.foreach_set('use_smooth',[True]*len(me.polygons))
    o=bpy.data.objects.new(name,me);col.objects.link(o);o.data.materials.append(M[mat])
    if sub:
        s=o.modifiers.new('sub','SUBSURF');s.levels=sub;s.render_levels=sub
    return o
# ---- head (context only) ----
R=.245;HC=Vector((0,0,.665))
CHIN=Vector((0,-.64,-.77)).normalized();NOSE=Vector((0,-1,-.3)).normalized()
def bump(d):
    d=Vector(d).normalized();a=d.angle(CHIN);b=d.angle(NOSE);return 1+.11*exp(-(a/.27)**2)+.07*exp(-(b/.085)**2)
def skull(d):
    x,y,z=d;ck=1+.055*exp(-((z+.3)/.4)**2);return Vector((x*1.03*ck,y*(.92 if y<0 else 1.0)*(1+.02*exp(-((z+.3)/.4)**2)),z*(.97 if z>0 else .9)))*R*bump(d)
def sphere_dirs(nu=40,nv=26):
    V=[Vector((0,0,1))];F=[]
    for i in range(1,nv):
        ph=i/nv*pi
        for j in range(nu):th=j/nu*2*pi;V.append(Vector((sin(ph)*cos(th),sin(ph)*sin(th),cos(ph))))
    V.append(Vector((0,0,-1)));b=len(V)-1
    for j in range(nu):F.append((0,1+j,1+(j+1)%nu));F.append((b,1+(nv-2)*nu+(j+1)%nu,1+(nv-2)*nu+j))
    for i in range(nv-2):
        for j in range(nu):F.append((1+i*nu+j,1+(i+1)*nu+j,1+(i+1)*nu+(j+1)%nu,1+i*nu+(j+1)%nu))
    return V,F
dv,df=sphere_dirs(96,64);head=mk('head',[HC+skull(d) for d in dv],df,'skin',sub=1)
def SK(az,ph,off=0):
    d=Vector((sin(az)*sin(ph),-cos(az)*sin(ph),cos(ph)));return HC+skull(d)+d*off
def decal(az,el,rx,rz,mat,off,dx=0,dz=0):
    d=Vector((sin(az)*cos(el),-cos(az)*cos(el),sin(el)));r=Vector((cos(az),sin(az),0));u=(Vector((0,0,1))-d*d.z).normalized();P=HC+skull(d)+d*.03;V=[P+r*dx+u*dz];F=[];n=28
    for k in range(1,6):
        for j in range(n):th=j/n*2*pi;V.append(P+r*(dx+cos(th)*rx*k/5)+u*(dz+sin(th)*rz*k/5))
    for j in range(n):F.append((0,1+j,1+(j+1)%n))
    for k in range(4):
        for j in range(n):F.append((1+k*n+j,1+(k+1)*n+j,1+(k+1)*n+(j+1)%n,1+k*n+(j+1)%n))
    o=mk('d',V,F,mat,sub=1);m=o.modifiers.new('sw','SHRINKWRAP');m.target=head;m.wrap_mode='ABOVE_SURFACE';m.offset=off;o.modifiers.move(1,0)
for sg in (1,-1):
    decal(sg*.43,-.16,.052,.064,'ink',.0012,dz=.004);decal(sg*.43,-.16,.044,.055,'eye',.0022);decal(sg*.43,-.16,.022,.03,'pupil',.0032,dz=.006);decal(sg*.43,-.16,.012,.013,'hl',.0042,dx=-sg*.013,dz=.028);decal(sg*.78,-.44,.04,.026,'pink',.0012)
# ---- strand = Bezier centre line + variable lens section + curled tip ----
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
STR={'mouth':[],'fringe':[],'side':[],'back':[],'ahoge':[]}
def strand(grp,K,w0,th0,curl=None,groove=.0,N=34,flat=.5):
    P=resample(bez(K),N);T,Nn=frames(P,P[0]-HC+Vector((0,0,.05)))
    if curl:
        ang,ln,cd=curl;tg=T[-1];c=Vector(cd);c=(c-tg*c.dot(tg)).normalized();p=P[-1].copy();Mc=18
        for j in range(1,Mc+1):
            th=ang*(j/Mc)**.9;p=p+(tg*cos(th)+c*sin(th))*(ln/Mc*(1.5-j/Mc));P.append(p.copy())
        T,Nn=frames(P,Nn[0])
    L=[0]
    for i in range(1,len(P)):L.append(L[-1]+(P[i]-P[i-1]).length)
    A=[];B=[]
    for i in range(len(P)):
        t=L[i]/L[-1];rt=.5+.5*ss(t/.1);A.append(max(.0012,w0*rt*(1-t**3.6)**.62));B.append(max(.0012,th0*rt*(1-t**4)**.55))
    STR[grp].append(dict(P=P,T=T,N=Nn,A=A,B=B,g=groove,flat=flat))
def strand_mesh(s,seg=16):
    V=[];F=[];P=s['P'];n=len(P)
    for i in range(n):
        w=s['T'][i].cross(s['N'][i]).normalized()
        for j in range(seg):
            th=j/seg*2*pi;x=cos(th);y=sin(th);y=y*(1-s['g']*exp(-x*x*7)) if y>0 else y*s['flat'];V.append(P[i]+w*(x*s['A'][i])+s['N'][i]*(y*s['B'][i]))
        if i:
            for j in range(seg):F.append(((i-1)*seg+j,(i-1)*seg+(j+1)%seg,i*seg+(j+1)%seg,i*seg+j))
    V.append(P[0]-s['T'][0]*s['B'][0]*.6);V.append(P[-1]+s['T'][-1]*.002);c=len(V)-2
    for j in range(seg):F.append((c,(j+1)%seg,j));F.append((c+1,(n-1)*seg+j,(n-1)*seg+(j+1)%seg))
    return V,F
def group_mesh(name,mat='hair'):
    V=[];F=[]
    for s in STR[name]:
        v,f=strand_mesh(s);b=len(V);V+=v;F+=[tuple(i+b for i in q) for q in f]
    return mk(name,V,F,mat,sub=1)
lerp=lambda a,b,t:a+(b-a)*t
def onskull(az0,az1,ph0,ph1,off,bulge=0,n=4,pw=1.4):
    return [SK(lerp(az0,az1,(k/n)**pw),lerp(ph0,ph1,k/n),off+bulge*sin(pi*k/n)) for k in range(n+1)]
for sg in (1,-1):
    K=[]
    for q in range(7):
        a=pi*q/6;d=Vector((sin(sg*.045+sg*.045*cos(a)),-1,-.46-.04*sin(a))).normalized();K.append(HC+skull(d)+d*.001)
    strand('mouth',K,.0045,.0045,flat=1,N=14)
HAIR=os.environ.get('HAIR','1')=='1'
# 1) FRINGE: nine leaf-shaped locks from the crown swirl over the forehead; tips reach the top of the eyes and flick sideways
for i,(a0,a1,ph,w,lay) in enumerate([(.0,.06,1.6,.034,1),(.2,.3,1.46,.046,0),(-.2,-.31,1.47,.046,0),(.42,.6,1.5,.05,1),(-.42,-.6,1.5,.05,1),(.66,.9,1.62,.05,0),(-.66,-.9,1.62,.05,0),(.1,.17,1.36,.03,1),(-.1,-.15,1.38,.03,1)]):
    sg=1 if a1>=a0 else -1;K=onskull(a0,a1,.07,ph,.014+.013*lay,bulge=.014)
    strand('fringe',K,w,.02,curl=(1.1,.045,(sg*cos(a1),sg*sin(a1),.0)),groove=.22 if w>.04 else 0)
# 2) SIDE: per side four locks over the temple, hanging in S-curves, J-curl outward
for sg in (1,-1):
    strand('side',onskull(sg*.8,sg*.97,.2,1.72,.02)+[(sg*.238,-.15,.555)],.034,.018,curl=(1.6,.05,(-sg,0,.1)))
    strand('side',onskull(sg*.92,sg*1.05,.08,1.5,.03,bulge=.008)+[(sg*.262,-.125,.5),(sg*.232,-.15,.41),(sg*.268,-.132,.32),(sg*.24,-.142,.25)],.05,.022,curl=(2.7,.085,(sg,-.25,.3)),groove=.25)
    strand('side',onskull(sg*1.25,sg*1.42,.07,1.55,.022)+[(sg*.3,-.03,.5),(sg*.27,-.05,.4),(sg*.325,-.03,.3),(sg*.292,-.05,.21)],.074,.027,curl=(2.9,.1,(sg,-.15,.3)),groove=.28)
    strand('side',onskull(sg*1.62,sg*1.8,.08,1.6,.034,bulge=.006)+[(sg*.305,.075,.5),(sg*.28,.095,.4),(sg*.335,.085,.3),(sg*.31,.1,.2),(sg*.33,.1,.15)],.072,.027,curl=(2.7,.095,(sg,.2,.3)),groove=.25)
# 3) BACK: two shingled layers, wave phase travels across neighbours so the flow reads as one stream; tips curl away from the centre line
def backlock(az,ph0,off,zs,rho0,w,th,phase,amp,curl,groove):
    ax,ay=sin(az),-cos(az);tx,ty=cos(az),sin(az);K=onskull(az,az,ph0,1.72,off,pw=1);z0=zs[0];z1=zs[-1]
    for j,z in enumerate(zs):
        u=(z0-z)/(z0-z1+1e-6);rr=rho0+.06*u+.014*cos(phase+j*1.9);wv=amp*sin(phase+j*1.9)*(.4+.6*u);K.append((ax*rr+tx*wv,.03+ay*rr*.92+ty*wv,z))
    sgn=1 if ax>.02 else (-1 if ax<-.02 else 1);strand('back',K,w,th,curl=(curl[0],curl[1],(ax*.5+sgn*abs(ay)*.9,ay*.5+.0,.38)),groove=groove,N=40)
for i in range(9):
    az=pi+(i-4)*.33;L=.13+.05*((i*5)%3)/2;backlock(az,.3,.016,[.5,.42,.34,.26,L+.06],.25,.086,.03,i*.85,.03,(2.8,.1),.3)
for i in range(8):
    az=pi+(i-3.5)*.33;L=.34+.05*((i*7)%3)/2;backlock(az,.06,.04,[.5,.44,L+.04],.285,.076,.028,i*.85+1.4,.024,(2.6,.085),.25)
# 4) AHOGE: one crescent
CR=Vector((0,.0,.895));strand('ahoge',[CR+Vector((0,.012,-.02)),CR+Vector((0,.04,.05)),CR+Vector((0,.02,.11)),CR+Vector((0,-.04,.135)),CR+Vector((0,-.09,.11)),CR+Vector((0,-.1,.075))],.03,.03,flat=1,N=30)
# base: scalp cap + neck curtain under the locks (so gaps read as grooves, not holes)
if HAIR:keep=[(d.z>.3 or (d.y>.05 and d.z>-.75)) for d in dv];mk('cap',[HC+skull(d)*1.025+Vector((0,.004,0)) for d in dv],[f for f in df if all(keep[i] for i in f)],'hairb',sub=1)
NS=sum(len(v) for v in STR.values())
if MODE=='curve':
    for g in STR:
        if g=='mouth':group_mesh(g,'mouth')
        elif HAIR:group_mesh(g)
else:
    # SDF sculpt: every strand sample is an oriented ellipsoid; smooth-union into a voxel field, marching cubes, light smooth
    from skimage import measure
    h=.0032;k=.007;lo=np.array([-.45,-.36,.03]);hi=np.array([.45,.5,1.08]);dim=np.ceil((hi-lo)/h).astype(int)+1;G=np.full(dim,.05,np.float32)
    for g in STR:
        for s in STR[g]:
            P=s['P']
            for i in range(len(P)):
                a=max(s['A'][i],.0045);b=max(s['B'][i]*(.5+s['flat']*.5),.0045);sp=(P[min(len(P)-1,i+1)]-P[max(0,i-1)]).length;l=max(sp*1.2,min(a,b));p=np.array(P[i]);ext=max(a,b,l)+k+h
                i0=np.maximum(0,np.floor((p-ext-lo)/h).astype(int));i1=np.minimum(dim,np.ceil((p+ext-lo)/h).astype(int)+1)
                if (i1<=i0).any():continue
                ax=[lo[d]+np.arange(i0[d],i1[d])*h-p[d] for d in range(3)];X,Y,Z=np.meshgrid(*ax,indexing='ij');w=np.array(s['T'][i].cross(s['N'][i]).normalized());nn=np.array(s['N'][i]);tg=np.array(s['T'][i])
                q=np.sqrt(((X*w[0]+Y*w[1]+Z*w[2])/a)**2+((X*nn[0]+Y*nn[1]+Z*nn[2])/b)**2+((X*tg[0]+Y*tg[1]+Z*tg[2])/l)**2);d1=((q-1)*min(a,b,l)).astype(np.float32)
                sub=G[i0[0]:i1[0],i0[1]:i1[1],i0[2]:i1[2]];hh=np.clip(.5+.5*(sub-d1)/k,0,1);G[i0[0]:i1[0],i0[1]:i1[1],i0[2]:i1[2]]=sub*(1-hh)+d1*hh-k*hh*(1-hh)
    v,f,_,_=measure.marching_cubes(G,0,spacing=(h,h,h));o=mk('sdfhair',[tuple(x+lo) for x in v],[tuple(int(i) for i in t[::-1]) for t in f],'hair');m=o.modifiers.new('sm','SMOOTH');m.factor=.5;m.iterations=4;print('SDFV',len(v))
# stand
sv=[];n=40
for j in range(n):a=j/n*2*pi;sv+=[(cos(a)*.42,sin(a)*.42+.04,.03),(cos(a)*.44,sin(a)*.44+.04,0)]
mk('stand',sv,[tuple(range(0,2*n,2))]+[(2*j,2*j+1,(2*j+3)%(2*n),(2*j+2)%(2*n)) for j in range(n)],'stand')
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.8,.79,.88,1);w.node_tree.nodes['Background'].inputs[1].default_value=.55
piv=bpy.data.objects.new('piv',None);col.objects.link(piv)
def light(loc,e,size,c=(1,1,1)):
    l=bpy.data.lights.new('l','AREA');l.energy=e;l.size=size;l.color=c;o=bpy.data.objects.new('L',l);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.55))-Vector(loc)).to_track_quat('-Z','Y').to_euler();o.parent=piv
light((-2.2,-2.2,2.6),110,1.6,(1,.96,.9));light((2.4,-1.6,1.0),16,3,(.9,.93,1));light((.8,2.6,2.2),40,2)
cam=bpy.data.cameras.new('cam');cam.type='ORTHO';co=bpy.data.objects.new('cam',cam);col.objects.link(co);sc.camera=co
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=True;sc.view_settings.view_transform='Standard'
def shot(name,ang,elev,scale=1.16,tz=.56):
    d=Vector((sin(ang)*cos(elev),-cos(ang)*cos(elev),sin(elev)));co.location=Vector((0,.04,tz))+d*6;co.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale;piv.rotation_euler=(0,0,ang)
    sc.render.resolution_x=560;sc.render.resolution_y=640;sc.render.filepath=os.path.join(OUT,'hr_%s%s_%s.png'%(MODE,'' if HAIR else 'bald',name));bpy.ops.render.render(write_still=True)
for n_,a,e in [('front',0,.03),('f34',-.6,.15),('side',pi/2,.03)]+([('back',pi,.03),('b34',pi-.65,.2),('top',.0,1.0)] if os.environ.get('ALL') else []):shot(n_,a,e,*((.8,.68) if os.environ.get('ZOOM') else ()))
print('STRANDS',NS,{g:len(v) for g,v in STR.items()})
