import bpy,bmesh,math,sys,os
from mathutils import Vector
from math import sin,cos,pi
OUT=os.path.dirname(os.path.abspath(__file__));Q=sys.argv[-1] if sys.argv[-1] in('draft','final') else 'draft'
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;col=sc.collection
# ---------------- materials: matte clay with faint surface grain ----------------
def clay(name,rgb,rough=.82,gloss=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;b=nt.nodes.get('Principled BSDF')
    c=[((int(rgb[i:i+2],16)/255)**2.2) for i in (1,3,5)]+[1]
    def S(k,v):
        i=b.inputs.get(k)
        if i is not None:i.default_value=v
    S('Base Color',c);S('Roughness',.18 if gloss else rough);S('Subsurface Weight',0 if gloss else .12);S('Subsurface Radius',(.08,.05,.04));S('Subsurface Scale',.05);S('Sheen Weight',0 if gloss else .25);S('Sheen Roughness',.5);S('Coat Weight',.5 if gloss else 0)
    if not gloss:
        n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=55;n.inputs['Detail'].default_value=6;bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.07;bp.inputs['Distance'].default_value=.004
        nt.links.new(n.outputs[0],bp.inputs['Height']);nt.links.new(bp.outputs[0],b.inputs['Normal'])
    return m
M={k:clay(k,v) for k,v in dict(skin='#ffe9da',hair='#e3c79d',navy='#3d3b58',ivory='#f6f0e4',gold='#dcb96c',white='#fbfaf6',pink='#ffaaa6',mouth='#c9786c',grass='#9ccf6a').items()}
for k,v in dict(ink='#352d4a',eye='#5f4aa0',eye2='#9a82dc',pupil='#43306e',hl='#ffffff').items():M[k]=clay(k,v,gloss=True)
# ---------------- mesh helpers (custom meshes, no primitives) ----------------
def mk(name,verts,faces,mat,sub=2,smooth=True):
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in verts],[],faces);me.update()
    if smooth:me.polygons.foreach_set('use_smooth',[True]*len(me.polygons))
    o=bpy.data.objects.new(name,me);col.objects.link(o);o.data.materials.append(M[mat])
    if sub:
        s=o.modifiers.new('sub','SUBSURF');s.levels=sub;s.render_levels=sub
    return o
def crom(P,n):
    P=[Vector(p) for p in P];P=[P[0]*2-P[1]]+P+[P[-1]*2-P[-2]];out=[];segs=len(P)-3
    for k in range(n+1):
        u=k/n*segs;i=min(int(u),segs-1);t=u-i;a,b,c,d=P[i],P[i+1],P[i+2],P[i+3]
        out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return out
def sweep(name,path,a,b,nf,mat,n=28,seg=12,sub=2,mod=None,build=True):
    """custom swept mesh: elliptical section (a across, b along the outward normal nf(p)), both functions of t in 0..1, rounded end caps"""
    pts=crom(path,n);V=[];F=[]
    for i,p in enumerate(pts):
        t=i/n;tg=(pts[min(n,i+1)]-pts[max(0,i-1)]).normalized();nn=nf(p,t) if callable(nf) else Vector(nf);nn=(nn-tg*nn.dot(tg));nn=nn.normalized() if nn.length>1e-6 else tg.orthogonal().normalized();w=tg.cross(nn).normalized()
        for j in range(seg):
            th=j/seg*2*pi;k=mod(t,th) if mod else 1;V.append(p+w*(a(t)*cos(th)*k)+nn*(b(t)*sin(th)*k))
        if i:
            for j in range(seg):F.append(((i-1)*seg+j,(i-1)*seg+(j+1)%seg,i*seg+(j+1)%seg,i*seg+j))
    t0=(pts[1]-pts[0]).normalized();t1=(pts[-1]-pts[-2]).normalized();V.append(pts[0]-t0*b(0)*.7);V.append(pts[-1]+t1*b(1)*.7);c0=len(V)-2
    for j in range(seg):F.append((c0,(j+1)%seg,j));F.append((c0+1,n*seg+j,n*seg+(j+1)%seg))
    return mk(name,V,F,mat,sub) if build else (V,F)
def loft(name,rings,mat,sub=2,mod=None):
    """vertical loft through rings (z, rx, ry[, cx, cy])"""
    zs=[r[0] for r in rings];z0,z1=zs[0],zs[-1];import bisect
    def at(t,idx):
        z=z0+(z1-z0)*t;i=min(len(rings)-2,max(0,bisect.bisect_right(zs,z)-1)) if z1>z0 else min(len(rings)-2,max(0,len(zs)-1-bisect.bisect_right(zs[::-1],z)));r0,r1=rings[i],rings[i+1];u=(z-r0[0])/((r1[0]-r0[0]) or 1);u=u*u*(3-2*u);return r0[idx]+(r1[idx]-r0[idx])*u if len(r0)>idx else 0
    path=[(at(k/8,3),at(k/8,4),z0+(z1-z0)*k/8) for k in range(9)]
    return sweep(name,path,lambda t:at(t,1),lambda t:at(t,2),(0,-1,0) if z1>z0 else (0,1,0),mat,n=20,seg=16,sub=sub,mod=mod)
def shrink(o,target,off):
    m=o.modifiers.new('sw','SHRINKWRAP');m.target=target;m.wrap_method='NEAREST_SURFACEPOINT';m.wrap_mode='ABOVE_SURFACE';m.offset=off;o.modifiers.move(len(o.modifiers)-1,0)
# ---------------- proportions ----------------
R=.245;HC=Vector((0,0,.665))
def skull(d,s=1.0):
    x,y,z=d;ck=1+.1*math.exp(-((z+.35)/.4)**2);fy=.94 if y<0 else 1.02;tp=1-.25*((-z-.6)/.4)**1.4 if z<-.6 else 1
    return Vector((x*ck*tp*1.04,y*fy*tp,z*.94))*R*s
def sphere_dirs(nu=32,nv=20):
    V=[Vector((0,0,1))];F=[]
    for i in range(1,nv):
        ph=i/nv*pi
        for j in range(nu):th=j/nu*2*pi;V.append(Vector((sin(ph)*cos(th),sin(ph)*sin(th),cos(ph))))
    V.append(Vector((0,0,-1)));b=len(V)-1
    for j in range(nu):F.append((0,1+j,1+(j+1)%nu));F.append((b,1+(nv-2)*nu+(j+1)%nu,1+(nv-2)*nu+j))
    for i in range(nv-2):
        for j in range(nu):F.append((1+i*nu+j,1+(i+1)*nu+j,1+(i+1)*nu+(j+1)%nu,1+i*nu+(j+1)%nu))
    return V,F
dv,df=sphere_dirs();head=mk('head',[HC+skull(d) for d in dv],df,'skin',sub=2)
def frame(az,el,s=1.0):
    d=Vector((sin(az)*cos(el),-cos(az)*cos(el),sin(el)));r=Vector((cos(az),sin(az),0));u=r.cross(d)*-1;u=(Vector((0,0,1))-d*d.z).normalized();return HC+skull(d,s),d,r,u
def decal(name,az,el,rx,rz,mat,off,dx=0,dz=0,rot=0,target=None,shape=None):
    P,d,r,u=frame(az,el);V=[P+d*.03+r*dx+u*dz];F=[];n=28;rings=5
    for k in range(1,rings+1):
        for j in range(n):
            th=j/n*2*pi;f=shape(th) if shape else 1;x=cos(th)*rx*k/rings*f;z=sin(th)*rz*k/rings*f;V.append(P+d*.03+r*(dx+x*cos(rot)-z*sin(rot))+u*(dz+x*sin(rot)+z*cos(rot)))
    for j in range(n):F.append((0,1+j,1+(j+1)%n))
    for k in range(rings-1):
        for j in range(n):F.append((1+k*n+j,1+(k+1)*n+j,1+(k+1)*n+(j+1)%n,1+k*n+(j+1)%n))
    o=mk(name,V,F,mat,sub=1);shrink(o,target or head,off);return o
# ---------------- face ----------------
for sg in (1,-1):
    az=sg*.44;el=-.17
    decal('lash',az,el,.047,.058,'ink',.0012,dz=.004,shape=lambda th:1+.1*max(0,sin(th)));decal('iris',az,el,.04,.05,'eye',.0022);decal('iris2',az,el,.032,.024,'eye2',.0032,dz=-.024);decal('pupil',az,el,.021,.029,'pupil',.0042,dz=.006)
    decal('hl',az,el,.011,.012,'hl',.0052,dx=-sg*.012,dz=.026);decal('hl2',az,el,.0055,.006,'hl',.0052,dx=sg*.013,dz=-.026)
    decal('flick',az,el,.009,.022,'ink',.0012,dx=sg*.05,dz=.03,rot=-sg*1.1);decal('blush',sg*.82,-.47,.04,.026,'pink',.0012)
P,d,r,u=frame(0,-.47)
for sg in (1,-1):sweep('mouth',[P+d*.004+r*(sg*.011+.011*cos(a))+u*(-.011*sin(a)*.9) for a in [pi*k/6 for k in range(7)]],lambda t:.0032,lambda t:.0032,d,'mouth',n=12,seg=8,sub=1)
# ---------------- body: lofted cloth forms ----------------
for sg in (1,-1):
    x=sg*.068
    loft('thigh',[(.2,.05,.05,x,0),(.3,.047,.047,x,0)],'skin');loft('sock',[(.075,.057,.057,x,0),(.14,.054,.054,x,0),(.2,.052,.052,x,0),(.215,.058,.058,x,0),(.225,.05,.05,x,0)],'white')
    sweep('shoe',[(x,.06,.05),(x,.0,.052),(x,-.06,.046),(x,-.1,.04)],lambda t:.062+.022*sin(t*pi)-(.012*t),lambda t:.04+.016*sin(t*pi),(0,0,1),'navy',n=14)
    sweep('strap',[(x-.06,-.02,.05),(x-.04,-.025,.094),(x,-.028,.104),(x+.04,-.025,.094),(x+.06,-.02,.05)],lambda t:.017,lambda t:.008,lambda p,t:Vector((p.x-x,0,p.z-.04)),'navy',n=12,seg=8)
    for k in range(5):
        a=k/5*2*pi;sweep('sf',[(x+cos(a)*.004,-.062,.092+sin(a)*.004),(x+cos(a)*.022,-.064,.092+sin(a)*.022)],lambda t:.009,lambda t:.005,(0,-1,.4),'gold',n=4,seg=8,sub=1)
loft('skirt',[(.345,.098,.092),(.31,.125,.118),(.25,.17,.162),(.2,.205,.196),(.192,.19,.182)],'navy',mod=lambda t,th:1+.07*sin(th*8)*t*t)
for k in range(6):
    a=-1.15+k*.46;sweep('sdot',[(sin(a)*.193,-cos(a)*.184,.222),(sin(a)*.2,-cos(a)*.191,.212)],lambda t:.011,lambda t:.007,(sin(a),-cos(a),0),'gold',n=4,seg=8,sub=1)
loft('jacket',[(.3,.132,.122),(.33,.128,.118),(.39,.108,.1),(.44,.086,.08),(.48,.055,.052)],'ivory',mod=lambda t,th:1+.03*sin(th*6)*(1-t)**2)
loft('trim',[(.292,.128,.118),(.3,.139,.129),(.312,.139,.129),(.32,.128,.118)],'navy')
sweep('vest',[(0,-.1,.325),(0,-.106,.37),(0,-.092,.42),(0,-.07,.455)],lambda t:.05-.012*t,lambda t:.02,(0,-1,0),'navy',n=10)
for z in (.34,.378):sweep('btn',[(0,-.118,z),(0,-.128,z)],lambda t:.011,lambda t:.011,(0,0,1),'gold',n=3,seg=8,sub=1)
for sg in (1,-1):
    sweep('collar',[(sg*.02,-.075,.468),(sg*.06,-.088,.45),(sg*.085,-.07,.42),(sg*.07,-.085,.395)],lambda t:.035*(1-.5*t),lambda t:.012,lambda p,t:Vector((p.x*.5,-1,.3)),'ivory',n=12)
    sweep('bow',[(sg*.012,-.125,.43),(sg*.05,-.14,.452),(sg*.085,-.13,.44),(sg*.075,-.125,.41),(sg*.03,-.128,.418)],lambda t:.02+.014*sin(t*pi),lambda t:.012,(0,-1,0),'navy',n=14)
    sweep('bowtail',[(sg*.01,-.128,.42),(sg*.03,-.132,.385),(sg*.045,-.128,.36)],lambda t:.016*(1-.3*t),lambda t:.008,(0,-1,0),'navy',n=8)
mk('gem',[(0,-.152,.458),(0,-.152,.398),(.022,-.15,.428),(-.022,-.15,.428),(0,-.166,.428),(0,-.138,.428)],[(0,2,4),(0,4,3),(1,4,2),(1,3,4),(0,5,2),(0,3,5),(1,2,5),(1,5,3)],'gold',sub=0,smooth=False).modifiers.new('bv','BEVEL').width=.003
sweep('knot',[(0,-.13,.44),(0,-.136,.428),(0,-.13,.416)],lambda t:.02,lambda t:.014,(0,-1,0),'navy',n=6)
for sg in (1,-1):
    sh=Vector((sg*.085,0,.455));el=Vector((sg*.15,-.02,.36));hd=Vector((sg*.185,-.035,.3))
    sweep('sleeve',[sh,(sh+el)/2+Vector((sg*.012,0,.01)),el,el+(hd-el)*.35],lambda t:.036+.034*t**1.3,lambda t:.034+.03*t**1.3,lambda p,t:Vector((0,-1,0)),'ivory',n=16,mod=lambda t,th:1+.04*sin(th*5)*t)
    sweep('cuff',[el+(hd-el)*.25,el+(hd-el)*.5],lambda t:.073,lambda t:.068,(0,-1,0),'navy',n=4);sweep('hand',[el+(hd-el)*.55,hd,hd+(hd-el)*.35],lambda t:.036+.012*sin(t*pi),lambda t:.032+.012*sin(t*pi),(0,-1,0),'skin',n=10)
    sweep('thumb',[hd+Vector((0,-.03,.0)),hd+Vector((-sg*.004,-.05,-.012))],lambda t:.014,lambda t:.014,(0,0,1),'skin',n=4,seg=8)
    c=[(sg*.03,.1,.44),(sg*.07,.13,.34),(sg*.085,.16,.24),(sg*.095,.185,.14),(sg*.1,.2,.075)]
    sweep('cape',c,lambda t:.062+.03*t-(.05*max(0,t-.82)/.18),lambda t:.013,lambda p,t:Vector((0,1,.25)),'navy',n=20)
    st=[];cz=.15;cx=sg*.094;cy=.2
    for k in range(8):
        a=k/8*2*pi;rr=.04 if k%2==0 else .014;st.append((cx+sin(a)*rr,cy+.0,cz+cos(a)*rr))
    V=[(p[0],p[1]+.004,p[2]) for p in st]+[(p[0],p[1]+.016,p[2]) for p in st]+[(cx,cy+.02,cz)];F=[tuple(range(7,-1,-1))]+[(k,(k+1)%8,8+(k+1)%8,8+k) for k in range(8)]+[(8+k,8+(k+1)%8,16) for k in range(8)]
    o=mk('star',V,F,'gold',sub=0,smooth=False);o.rotation_euler=(-.18,0,0)
loft('capeback',[(.47,.06,.05,0,.06),(.42,.1,.05,0,.085),(.36,.12,.04,0,.11)],'ivory')
# ---------------- hair: every lock is a hand-shaped ribbon that starts at the crown, flows over the skull and hangs; all locks are fused with a voxel remesh and smoothed like clay ----------------
HV=[];HF=[]
def addm(vf):
    V,F=vf;b=len(HV);HV.extend(V);HF.extend([tuple(i+b for i in f) for f in F])
CR=Vector((0,.045,HC.z+R*.985))
def sk(az,ph,s=1.045):
    d=Vector((sin(az)*sin(ph),-cos(az)*sin(ph),cos(ph)));return HC+skull(d,s)+Vector((0,.012,.008))
def lockpath(az,ph_end,sweepaz=0,hang=None,lift=0):
    P=[CR.copy()];n=5
    for k in range(1,n+1):
        t=k/n;P.append(sk(az+sweepaz*t*t,ph_end*t,1.09+lift*sin(t*pi)))
    if hang:P+= [Vector(h) for h in hang]
    return P
def nrm(p,t):
    v=p-HC if p.z>HC.z-R*.6 else Vector((p.x,p.y-.02,0));v=Vector((v.x,v.y,v.z*.8));return v.normalized() if v.length>1e-5 else Vector((0,-1,0))
def lock(az,ph_end,w,th,sweepaz=0,hang=None,lift=0,tipr=.5,n=30):
    w*=.6;th*=.72;P=lockpath(az,ph_end,sweepaz,hang,lift)
    a=lambda t:w*(.22+.78*min(1,t*3.2))*(1 if t<.8 else max(tipr*.5,math.sqrt(max(0,1-((t-.8)/.2)**2*(1-tipr*tipr*.25)))))
    b=lambda t:th*(.5+.5*min(1,t*3))*(1 if t<.85 else max(.4,math.sqrt(max(0,1-((t-.85)/.15)**2*.84))))
    addm(sweep('l',P,a,b,nrm,'hair',n=n,seg=14,build=False))
# scalp mass under the locks (keeps the union solid; sits behind the face surface)
sv=[HC+Vector((0,.05,.03))+skull(d,1.02) for d in dv];addm((sv,[tuple(f) for f in df]))
# fringe: broad locks sweeping from the crown over the forehead, tips curling in around the eyes
for az,ph,w,sw,tip in [(-.02,1.32,.055,.05,.5),(.3,1.2,.07,-.22,.5),(-.3,1.22,.07,.24,.5),(.62,1.32,.075,-.16,.45),(-.62,1.34,.075,.18,.45),(.14,1.08,.045,.18,.5),(-.15,1.1,.045,-.2,.5)]:
    lock(az,ph,w,.028,sweepaz=sw,lift=.035,tipr=tip)
# face-framing side locks: over the temple, then down in soft S-waves to the hip, tips curling outward
for sg in (1,-1):
    lock(sg*1.0,1.45,.075,.032,sweepaz=-sg*.12,lift=.03,hang=[(sg*.275,-.1,.5),(sg*.25,-.13,.4),(sg*.3,-.1,.31),(sg*.275,-.12,.23),(sg*.33,-.14,.19)])
    lock(sg*1.38,1.5,.085,.036,lift=.03,hang=[(sg*.31,-.02,.5),(sg*.285,-.04,.39),(sg*.345,-.01,.29),(sg*.31,-.04,.2),(sg*.37,-.05,.14),(sg*.4,-.07,.17)])
    lock(sg*.78,1.25,.05,.024,sweepaz=-sg*.2,lift=.03,hang=[(sg*.225,-.165,.54),(sg*.2,-.175,.47)])
# back curtain: wide overlapping locks, alternating wave phase, to knee level with rounded curled tips
import random;random.seed(4);NB=15
for k in range(NB):
    t=k/(NB-1);az=pi*(.58+.84*t);ax=sin(az);ay=-cos(az);ph=k*2.1;L=.13+.07*abs(sin(k*1.7));rad=lambda z:.25+.12*(1-(z-.1)/.5)
    hang=[]
    for j,z in enumerate([.5,.41,.32,.24,L+.04,L]):
        rr=.235+.012*(k%2)+.075*(1-(z-L)/(.5-L+1e-6))+.022*sin(ph+j*1.5);tx=cos(az);ty=sin(az);wv=.04*sin(ph+j*1.45);hang.append((ax*rr+tx*wv,ay*rr*.9+ty*wv+.03,z))
    hang.append((hang[-1][0]+ax*.035,hang[-1][1]+ay*.035,L+.03))
    lock(az,1.5,.095,.04,lift=.035,hang=hang,tipr=.7,n=36)
# ahoge: one tapered banana curl
ah=[CR+Vector((0,.01,-.03)),CR+Vector((0,.035,.04)),CR+Vector((0,.015,.1)),CR+Vector((0,-.04,.125)),CR+Vector((0,-.085,.105)),CR+Vector((0,-.1,.07))]
addm(sweep('ah',ah,lambda t:.034*(1-t)**.6+.004,lambda t:.032*(1-t)**.6+.004,(1,0,0),'hair',n=24,build=False))
hair=mk('hair',HV,HF,'hair',sub=0);bpy.context.view_layer.objects.active=hair;hair.select_set(True)
hair.data.remesh_voxel_size=.006 if Q=='final' else .0075;bpy.ops.object.voxel_remesh();hair.data.polygons.foreach_set('use_smooth',[True]*len(hair.data.polygons))
sm=hair.modifiers.new('sm','SMOOTH');sm.factor=.5;sm.iterations=3 if Q=='final' else 2;s2=hair.modifiers.new('sub','SUBSURF');s2.levels=1;s2.render_levels=1
# ---------------- flower, star, ribbon on the character's left ----------------
def hframe(az,el,s):
    d=Vector((sin(az)*cos(el),-cos(az)*cos(el),sin(el)));r=Vector((cos(az),sin(az),0));u=(Vector((0,0,1))-d*d.z).normalized();return HC+skull(d,s),d,r,u
P,d,r,u=hframe(.92,.5,1.2)
for k in range(5):
    a=k/5*2*pi+.3;c=P+r*cos(a)*.012+u*sin(a)*.012;e=P+r*cos(a)*.085+u*sin(a)*.085+d*.004
    sweep('petal',[c,(c+e)/2+d*.012,e],lambda t:.012+.034*sin(t*pi)**.7,lambda t:.012+.006*sin(t*pi),d,'white',n=10)
sweep('fc',[P+d*.006,P+d*.022],lambda t:.022,lambda t:.022,u,'white',n=3)
st=[]
for k in range(8):
    a=k/8*2*pi;rr=.042 if k%2==0 else .014;st.append(P+d*.026+r*sin(a)*rr+u*cos(a)*rr)
mk('fstar',st+[p+d*.01 for p in st]+[P+d*.044],[tuple(range(8))]+[(k,(k+1)%8,8+(k+1)%8,8+k) for k in range(8)]+[(8+k,8+(k+1)%8,16) for k in range(8)],'gold',sub=0,smooth=False)
B=P-u*.045+r*.05-d*.012
for a,l in ((-.25,.11),(-.8,.1)):
    e=B+r*cos(a)*l+u*sin(a)*l;mid=(B+e)/2;pp=Vector((-sin(a),cos(a),0));pv=r*pp.x+u*pp.y
    sweep('rloop',[B,mid+pv*.03+d*.012,e,mid-pv*.03+d*.012,B],lambda t:.02,lambda t:.008,d,'navy',n=18,seg=10)
for a,l in ((-1.35,.15),(-1.75,.13)):
    e=B+r*cos(a)*l+u*sin(a)*l-d*.02;sweep('rtail',[B,(B+e)/2+d*.008,e],lambda t:.022*(1-.25*t),lambda t:.008,d,'navy',n=10,seg=10)
sweep('rknot',[B-u*.012,B+u*.012],lambda t:.018,lambda t:.014,d,'navy',n=3)
# ---------------- base, light, cameras ----------------
bv=[];bf=[];nb=48
for k in range(nb):a=k/nb*2*pi;bv+= [(cos(a)*.5,sin(a)*.5,0),(cos(a)*.52,sin(a)*.52,-.05)]
bf=[tuple(range(0,2*nb,2))]+[(2*k,2*k+1,(2*k+3)%(2*nb),(2*k+2)%(2*nb)) for k in range(nb)];mk('base',bv,bf,'grass',sub=0)
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.82,.8,.9,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45
def light(kind,loc,e,size,colr=(1,1,1)):
    l=bpy.data.lights.new(kind,'AREA');l.energy=e;l.size=size;l.color=colr;o=bpy.data.objects.new('L',l);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.5))-Vector(loc)).to_track_quat('-Z','Y').to_euler();return o
LK=light('key',(-1.6,-2.6,2.6),95,2.2,(1,.96,.9));LF=light('fill',(2.4,-1.6,1.2),22,3,(.9,.93,1));LR=light('rim',(.8,2.6,2.2),45,2)
cam=bpy.data.cameras.new('cam');cam.type='ORTHO';co=bpy.data.objects.new('cam',cam);col.objects.link(co);sc.camera=co
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=96 if Q=='final' else 28;sc.cycles.use_denoising=True;sc.render.film_transparent=False;sc.view_settings.view_transform='Standard'
piv=bpy.data.objects.new('piv',None);col.objects.link(piv)
for L in (LK,LF,LR):L.parent=piv
def shot(name,ang,elev,scale,tz,w,h):
    d=Vector((sin(ang)*cos(elev),-cos(ang)*cos(elev),sin(elev)));co.location=Vector((0,0,tz))+d*6;co.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=scale;piv.rotation_euler=(0,0,ang)
    sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=os.path.join(OUT,'h_%s.png'%name);bpy.ops.render.render(write_still=True)
k=1 if Q=='final' else .6
shot('hero',-.5,.16,1.5,.54,int(930*k),int(1500*k));shot('front',0,.02,1.5,.54,int(510*k),int(735*k));shot('side',pi/2,.02,1.5,.54,int(510*k),int(735*k));shot('back',pi,.02,1.5,.54,int(500*k),int(735*k))
shot('face',0,.02,.68,.68,int(510*k),int(735*k));shot('acc',.75,.1,.8,.74,int(510*k),int(735*k));shot('back34',pi-.6,.25,1.5,.54,int(500*k),int(735*k))
print('HAIRV',len(hair.data.vertices))
