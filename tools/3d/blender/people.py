import bpy,sys,os
import numpy as np
from mathutils import Vector,Euler,Matrix
from math import sin,cos,pi
from skimage import measure
OUT=os.path.dirname(os.path.abspath(__file__));VI=int(sys.argv[-1])
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;col=sc.collection
def clay(name,rgb):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;b=nt.nodes.get('Principled BSDF');c=[((int(rgb[i:i+2],16)/255)**2.2) for i in (1,3,5)]+[1]
    for k,v in (('Base Color',c),('Roughness',.85),('Subsurface Weight',.1),('Subsurface Radius',(.1,.06,.04)),('Subsurface Scale',.05),('Sheen Weight',.35),('Sheen Roughness',.6)):
        if b.inputs.get(k) is not None:b.inputs[k].default_value=v
    n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=90;n.inputs['Detail'].default_value=8;bp=nt.nodes.new('ShaderNodeBump');bp.inputs['Strength'].default_value=.12;bp.inputs['Distance'].default_value=.004;nt.links.new(n.outputs[0],bp.inputs['Height']);nt.links.new(bp.outputs[0],b.inputs['Normal'])
    m['hex']=rgb;return m
def mk(name,V,F,mat,sub=0):
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in V],[],F);me.update();me.polygons.foreach_set('use_smooth',[True]*len(me.polygons));o=bpy.data.objects.new(name,me);col.objects.link(o);o.data.materials.append(mat)
    if sub:
        s=o.modifiers.new('s','SUBSURF');s.levels=sub;s.render_levels=sub
    return o
def e(c,r,eu=(0,0,0),p=2):
    r=(r,r,r) if isinstance(r,(int,float)) else r;return (np.array(c,float),np.array(r,float),np.array(Euler(eu,'XYZ').to_matrix()),p)
def sdf(pts,plist,k):
    d=np.full(pts.shape[:-1],1.0,np.float32)
    for c,r,Rm,p in plist:
        if isinstance(p,tuple):
            q=(pts-c)@Rm;z=q[...,2];rx=np.interp(z,p[0],p[1]);ry=np.interp(z,p[0],p[2]);d1=np.maximum((np.sqrt((q[...,0]/rx)**2+(q[...,1]/ry)**2)-1)*np.minimum(rx,ry),np.maximum(p[0][0]-z,z-p[0][-1])).astype(np.float32)
        else:q=np.abs((pts-c)@Rm)/r;d1=(((q**p).sum(-1)**(1/p)-1)*r.min()).astype(np.float32)
        if k:h=np.clip(.5+.5*(d-d1)/k,0,1);d=d*(1-h)+d1*h-k*h*(1-h)
        else:d=np.minimum(d,d1)
    return d
both=lambda f:[f(1),f(-1)]
def loft(prof,ysc=.84,sc=1.0):
    zs=np.array([a for a,b in prof]);rs=np.array([b for a,b in prof]);zd=np.linspace(zs[0],zs[-1],240);rd=np.interp(zd,zs,rs);ker=np.exp(-np.linspace(-2,2,31)**2);ker/=ker.sum();rd=np.convolve(np.pad(rd,15,mode='edge'),ker,mode='valid')
    return (np.zeros(3),np.ones(3),np.eye(3),(zd,rd*sc,rd*sc*ysc))
ARM=[];HAND=[];LEG=[];UP=-.01 if VI==4 else .06;LEGH=.055 if VI==4 else .085;LW=.027 if VI==4 else .036;AW=.026 if VI==4 else .036;HW=.033 if VI==4 else .04
def arms(x,z,l=.1,a=.5,w=.055,y=0):
    for s in (1,-1):
        c=Vector((s*(x+.025),y,z+UP));Rm=Euler((0,-s*a,0),'XYZ').to_matrix();ARM.append(e(tuple(c),(AW,AW,l),(0,-s*a,0)));HAND.append(e(tuple(c+Rm@Vector((0,0,-l-.012))),HW))
    return []
def hands(x,z,r=.05,y=0,keep=False):
    if keep:HAND.extend(both(lambda s:e((s*x,y,z+UP),.04)))
    return []
def feet(x=.08,r=(.075,.1,.05),y=-.02):
    x=min(x,.085) if VI!=4 else .05;LEG.extend(both(lambda s:e((s*x,0,LEGH),(LW,LW,LEGH))));return both(lambda s:e((s*x,y,r[2]*.9),(min(r[0],.07),min(r[1],.095),r[2])))
def shell(hz,hr,p=2,g=1.11):return e((0,.015,hz+.02),tuple(v*g for v in hr),p=p)
# ---------- ten silhouettes (1.5 heads tall: head ~0.6, body ~0.3) ----------
VAR=int(os.environ.get('VAR','0'))
def var4(v,k):
    HR0=(.27,.28,.29);HS=lambda g:shell(.6,HR0,4,g);box_lo=lambda z:e((0,0,z-.5),(.6,.6,.5),p=8);box_hi=lambda z:e((0,0,z+.5),(.6,.6,.5),p=8)
    FACE=lambda top=.7:e((0,-.33,(top+.3)/2),(.24,.2,(top-.3)/2),p=2.6)
    RD=lambda g=1.0,p=3,dz=0:e((0,.012,.665+dz),(.32*g,.33*g,.3*g),p=p)
    SC=lambda z0=.35,z1=.58:both(lambda s:e((s*.34,-.07,(z0+z1)/2),(.11,.12,(z1-z0)/2),p=2.4))
    FR=lambda n=4,z=.7,w=.085:[e((x,-.3,z),(w,.04,.06)) for x in np.linspace(-.17,.17,n)]
    v['hat']=[];v['hatcut']=[];v['hair2']=[];v['pt']='shorts';v['hair']=[];v['cut']=[];v['hairx']=[]
    SK=['#ffd9c0','#f3c6a4','#d9a27c','#ffe6d6','#c98d68']
    if k==1:  # cap + short hair under it
        v['hat']=[RD(1.05,2.8,.01)];v['hatcut']=[box_lo(.69)];v['hatx']=[e((0,-.32,.705),(.19,.16,.025))];v['hair']=[RD(1.0)];v['cut']=[FACE(.72),box_lo(.5)]
        C=dict(skin=SK[0],top='#f2c14e',shoe='#3f4a6b',hair='#4a3528',hat='#3f6fb5',pants='#6f8fc0')
    if k==2:  # bowl cut, long chinos
        v['hair']=[RD(1.06,2.5,.015)];v['hairx']=FR(5,.7,.075);v['cut']=[FACE(.72),box_lo(.5)];v['pt']='long'
        C=dict(skin=SK[0],top='#8cc7a0',shoe='#5a4636',hair='#2f2a28',pants='#c9b48a')
    if k==3:  # bob + dress
        v['hair']=[RD(1.03,2.6),e((0,.15,.52),(.3,.18,.15),p=2.3)];v['hairx']=FR(3,.69,.1)+both(lambda s:e((s*.292,-.14,.5),(.062,.095,.135),(0,-s*.12,0)));v['cut']=[FACE(.69),box_lo(.38)]+SC(.3,.59);v['pt']='skirt'
        C=dict(skin=SK[3],top='#f4a7b4',shoe='#c0607a',hair='#7a4a32',pants='#f4a7b4')
    if k==4:  # twin pigtails + skirt
        v['hair']=[RD(1.01)];v['hairx']=both(lambda s:e((s*.37,.06,.55),(.075,.07,.12),(0,s*.3,0)))+both(lambda s:e((s*.33,.05,.66),.055))+FR(4,.7,.07);v['cut']=[FACE(.7),box_lo(.53)];v['pt']='skirt'
        C=dict(skin=SK[0],top='#b79be0',shoe='#4a3a6a',hair='#c2733e',pants='#5a4a8a')
    if k==5:  # beanie with pom, long pants
        v['hat']=[RD(1.1,2.8,.02),e((0,.01,1.0),.065)];v['hatcut']=[box_lo(.68)];v['hatx']=[e((0,.012,.69),(.355,.365,.04),p=2.8)];v['hair']=[RD(1.0)];v['hairx']=FR(4,.655,.07);v['cut']=[FACE(.74),box_lo(.52)];v['pt']='long'
        C=dict(skin=SK[1],top='#e46a5e',shoe='#2f2f36',hair='#2a2420',hat='#f0e6d2',pants='#444a5c')
    if k==6:  # buzz cut
        v['hair']=[RD(.99,3.3,.01)];v['cut']=[FACE(.77),box_lo(.48)]
        C=dict(skin=SK[4],top='#f7f4ee',shoe='#e8e4dc',hair='#1f1a18',pants='#3a3a40')
    if k==7:  # ponytail, long jeans
        v['hair']=[RD(1.02)];v['hairx']=[e((0,.34,.72),(.06,.07,.06)),e((0,.39,.58),(.07,.065,.14),(.3,0,0))]+FR(3,.7,.09);v['cut']=[FACE(.7),box_lo(.52)];v['pt']='long'
        C=dict(skin=SK[0],top='#9fd8d0',shoe='#f2f0ea',hair='#3b2a22',pants='#5f7fb0')
    if k==8:  # grey bun + long skirt
        v['hair']=[RD(1.03,2.6)];v['hairx']=[e((0,.1,.96),(.11,.11,.085))];v['cut']=[FACE(.72),box_lo(.52)];v['pt']='longskirt'
        C=dict(skin=SK[3],top='#d8c3a5',shoe='#6a5040',hair='#cfcac6',pants='#7a6a8a')
    if k==9:  # curly
        L=[]
        for a in range(14):
            for b in range(4):
                ph=.35+b*.33;az=a/14*2*pi+b*.2;L.append(e((sin(az)*sin(ph)*.29,cos(az)*sin(ph)*.29,.64+cos(ph)*.27),.075))
        L.append(e((0,0,.92),.09));v['hair']=[RD(.99)]+L;v['cut']=[FACE(.71),box_lo(.48)]
        C=dict(skin=SK[2],top='#f39a4a',shoe='#3a3a3a',hair='#2a201c',pants='#2f5f8a')
    if k==10:  # straw hat
        v['hat']=[e((0,.01,.8),(.33,.34,.22),p=2.4),e((0,0,.72),(.46,.46,.022))];v['hatcut']=[box_lo(.7)];v['hatx']=[e((0,.01,.75),(.335,.345,.03),p=2.4)];v['hair']=[RD(1.0)];v['cut']=[FACE(.72),box_lo(.5),box_hi(.73)]
        C=dict(skin=SK[1],top='#7fb5e8',shoe='#8a5a3a',hair='#5a3a26',hat='#e8cf8a',pants='#9a7a5a')
    if k==11: # long straight
        v['hair']=[RD(1.03,2.6),e((0,.15,.44),(.29,.16,.23),p=2.4)];v['hairx']=FR(4,.7,.075)+both(lambda s:e((s*.29,-.12,.45),(.055,.08,.2)));v['cut']=[FACE(.7),box_lo(.2)]+SC(.2,.59);v['pt']='long'
        C=dict(skin=SK[0],top='#f7f4ee',shoe='#3a3a44',hair='#2b2422',pants='#5f7fb0')
    if k==12: # long wavy, side-swept fringe
        L=[]
        for j,z in enumerate((.6,.5,.4,.31)):
            for x in (-.2,-.07,.07,.2):L.append(e((x+.025*sin(j*1.7+x*9),.17+.03*cos(j*1.3+x*7),z),(.095,.1,.085)))
        L+=[e((s*(.29+.018*(-1)**j),-.1,z),(.06,.075,.072)) for s in (1,-1) for j,z in enumerate((.58,.49,.4,.32))]
        v['hair']=[RD(1.03,2.6),e((0,.15,.48),(.28,.16,.2),p=2.4)];v['hairx']=L+[e((.06,-.3,.71),(.2,.045,.06),(0,.35,0))];v['cut']=[FACE(.7),box_lo(.3)]+SC(.25,.59);v['pt']='skirt'
        C=dict(skin=SK[1],top='#f6c1d0',shoe='#8a4a5a',hair='#9a5a2c',pants='#6b8ec4')
    v['C']=C;v.setdefault('hatx',[])
    TP=[(.125,.064),(.138,.087),(.16,.09),(.2,.087),(.24,.074),(.268,.056),(.285,.036),(.292,.02)]
    if v['pt'] in ('skirt','longskirt'):
        lo_=.075 if v['pt']=='skirt' else .02;v['pants']=[loft([(lo_,.115),(lo_+.03,.11),(.16,.09)]+TP[3:],sc=.98)];v['pantscut']=[box_hi(.16)]
    return v
def variant(i):
    v=dict(pantscut=[],pants=[],skin=[],cloth=[],clothcut=[],shoe=[],hair=[],cut=[],hairx=[],eye=(.42,-.05),hz=.62)
    if i==1:   # ball head + bean body, bowl cut
        hr=(.33,.3,.31);v.update(col=('#ffdcc8','#8fb8e8','#5a4a45','#5b4336'));v['skin']=[e((0,0,.62),hr)]+hands(.235,.16);v['cloth']=[e((0,0,.2),(.17,.14,.2))]+arms(.19,.24);v['shoe']=feet();v['hair']=[shell(.62,hr)];v['cut']=[e((0,-.32,.55),(.3,.22,.2))]
    if i==2:   # wide mochi head + tiny cone body, top bun
        hr=(.4,.31,.27);v.update(hz=.55,eye=(.46,-.02),col=('#ffe2d0','#f4a7a0','#7a5a50','#3d3340'));v['skin']=[e((0,0,.55),hr)]+hands(.2,.19,.045,-.02);v['cloth']=[e((0,0,.17),(.14,.12,.17)),e((0,0,.08),(.19,.16,.09))]+arms(.15,.21,.07,.6);v['shoe']=feet(.07,(.06,.08,.04));v['hair']=[shell(.55,hr)];v['cut']=[e((0,-.33,.47),(.37,.24,.22))];v['hairx']=[e((0,.03,.87),(.14,.14,.11))]
    if i==3:   # tall egg head + pill body, side-swept
        hr=(.29,.28,.36);v.update(hz=.66,eye=(.4,-.12),col=('#f6d2b8','#a8d5a2','#4a4a5a','#c98b4a'));v['skin']=[e((0,0,.66),hr)]+hands(.17,.12,.045);v['cloth']=[e((0,0,.2),(.13,.12,.2))]+arms(.15,.2,.1,.2,.05);v['shoe']=feet(.07);v['hair']=[shell(.66,hr)];v['cut']=[e((.1,-.3,.55),(.3,.22,.24),(0,.4,0))]
    if i==4:   # rounded-square head + block body, cap
        hr=(.27,.28,.29);v.update(hz=.6,col=('#ffd9c0','#f2c14e','#3f4a6b','#3f6fb5'));v['skin']=[e((0,0,.64),(.27,.28,.25),p=4),e((0,-.005,.53),(.21,.235,.12),p=3),e((0,0,.3),(.04,.04,.03))]+hands(.23,.15);TP=[(.125,.064),(.138,.087),(.16,.09),(.2,.087),(.24,.074),(.268,.056),(.285,.036),(.292,.02)];v['cloth']=[loft(TP),e((0,0,.278),(.05,.046,.012))]+arms(.07,.225,.05,.4);v['clothcut']=[e((0,0,.152-.5),(.5,.5,.5),p=8)];v['pants']=[loft([(.13,.064),(.14,.088)]+TP[2:],sc=.97)]+both(lambda s:e((s*.049,0,.125),(.038,.04,.05)));v['pantscut']=[e((0,0,.16+.5),(.5,.5,.5),p=8),e((0,0,.1-.5),(.5,.5,.5),p=8)];v['shoe']=feet(.055,(.034,.05,.027));v['hair']=[shell(.6,hr,4,1.08)];v['cut']=[e((0,0,.36),(.6,.6,.33),p=6)];v['hairx']=[e((0,-.3,.71),(.18,.15,.03))]
    if i==5:   # pear head (low cheeks) + flared dress, twin buns
        v.update(hz=.58,eye=(.42,.0),col=('#ffe0cf','#c9a7e8','#6a4a6a','#6b4a3a'));v['skin']=[e((0,0,.68),(.27,.26,.26)),e((0,0,.54),(.36,.29,.2))]+hands(.2,.2,.045);v['cloth']=[e((0,0,.23),(.11,.1,.13)),e((0,0,.1),(.22,.19,.11))]+arms(.16,.26,.08,.6,.045);v['shoe']=feet(.07,(.055,.075,.04));v['hair']=[e((0,.02,.7),(.3,.29,.28)),e((0,.03,.56),(.385,.3,.2))];v['cut']=[e((0,-.34,.52),(.33,.25,.25))];v['hairx']=both(lambda s:e((s*.33,.04,.88),(.13,.12,.12)))
    if i==6:   # wide oval head with ears + ball body on little legs, buzz cut
        hr=(.38,.29,.29);v.update(hz=.64,eye=(.44,-.06),col=('#eec3a0','#f08c5a','#404040','#2e2a2a'));v['skin']=[e((0,0,.64),hr)]+both(lambda s:e((s*.385,.0,.6),(.06,.045,.085)))+hands(.21,.2,.045);v['cloth']=[e((0,0,.23),(.15,.13,.13))]+arms(.17,.26,.07,.7,.045);v['shoe']=feet(.075,(.065,.09,.04));v['hair']=[shell(.64,hr,2,1.035)];v['cut']=[e((0,-.3,.52),(.42,.26,.3))]
    if i==7:   # round head + bell poncho, beanie with pom
        hr=(.32,.3,.3);v.update(hz=.64,col=('#ffdcc8','#e86a6a','#5a4040','#4f8f7a'));v['skin']=[e((0,0,.64),hr)]+hands(.22,.1,.042,-.08,keep=True);v['cloth']=[e((0,0,.27),(.13,.12,.13)),e((0,0,.13),(.26,.22,.13))];v['shoe']=feet(.08,(.06,.085,.04),-.03);v['hair']=[shell(.64,hr,2,1.09)];v['cut']=[e((0,0,.4),(.6,.6,.32),p=6)];v['hairx']=[e((0,.015,.735),(.355,.335,.05)),e((0,.02,1.02),.075)]
    if i==8:   # flat-top barrel head + small block body, mop
        hr=(.3,.28,.28);v.update(hz=.6,eye=(.4,-.1),col=('#f9cfae','#7fc8c0','#4a4a4a','#8a5a2e'));v['skin']=[e((0,0,.6),hr,p=5)]+hands(.2,.14,.045);v['cloth']=[e((0,0,.18),(.15,.12,.17),p=4)]+arms(.17,.21,.09,.3,.05);v['shoe']=feet(.07);v['hair']=[shell(.6,hr,5,1.06)];v['cut']=[e((0,-.34,.5),(.27,.25,.2),p=4)];v['hairx']=[e((0,.0,.88),(.31,.29,.07),p=4)]
    if i==9:   # peach head with small chin + tiny body, big shoes, ponytail
        v.update(hz=.63,eye=(.42,-.04),col=('#ffe4d6','#f7d86a','#c05a5a','#e8b96a'));v['skin']=[e((0,0,.65),(.33,.3,.29)),e((0,-.02,.44),(.15,.17,.12))]+hands(.16,.16,.04);v['cloth']=[e((0,0,.19),(.11,.1,.14))]+arms(.13,.22,.07,.4,.04);v['shoe']=feet(.1,(.1,.14,.055),-.04);v['hair']=[shell(.65,(.33,.3,.29))];v['cut']=both(lambda s:e((s*.15,-.33,.55),(.2,.24,.24),(0,-s*.3,0)));v['hairx']=[e((0,.36,.76),(.09,.1,.09)),e((0,.43,.6),(.07,.07,.14))]
    if i==10:  # gumdrop: hood fused to body, round hood ears
        v.update(hz=.6,eye=(.42,-.03),col=('#ffdcc8','#b7d37a','#6a5a40','#5b4336'));v['skin']=[e((0,0,.6),(.3,.28,.28))]+hands(.25,.2,.045,-.04);v['cloth']=[e((0,.02,.62),(.36,.33,.34)),e((0,0,.2),(.27,.23,.22))]+both(lambda s:e((s*.23,.0,.94),(.09,.06,.08)))+arms(.25,.25,.07,.5);v['clothcut']=[e((0,-.38,.6),(.27,.22,.25))];v['shoe']=feet(.1,(.075,.1,.045),-.03);v['hairx']=[e((0,-.24,.8),(.14,.05,.05),(.3,0,0))]
    if i==4 and VAR:v=var4(v,VAR)
    HR={1:(.33,.3,.31),2:(.4,.31,.27),3:(.29,.28,.36),4:(.27,.28,.22),5:(.36,.29,.3),6:(.38,.29,.29),7:(.32,.3,.3),8:(.3,.28,.28),9:(.33,.3,.3),10:(.3,.28,.28)}[i];hz=v['hz']
    if i==6:v['skin']=[v['skin'][0]]
    v['skin']=v['skin'][:1]+[e((0,-HR[1]*.66,hz-HR[2]*.6),(.1,.085,.075))]+v['skin'][1:]
    ears=both(lambda s:e((s*(HR[0]+.012),.02,hz-.04),(.058,.04,.075)));v['ears']=ears
    if i!=10:v['cut']=v['cut']+both(lambda s:e((s*(HR[0]+.02),-.03,hz-.035),(.1,.13,.11)))
    HD=-.085 if i==4 else 0
    for kk in ('pantscut','pants','skin','cloth','clothcut','hair','cut','hairx','ears','hat','hatcut','hatx'):
        if kk not in v:continue
        v[kk]=[(c+np.array([0,0,UP+(HD if (kk in ('hair','cut','hairx','ears','hat','hatcut','hatx') or (kk=='skin' and j<3)) else 0)]),r,Rm,p) for j,(c,r,Rm,p) in enumerate(v[kk])]
    v['hz']=hz+UP+HD;return v
V=variant(VI)
if 'C' in V:C=V['C'];V['col']=(C['skin'],C['top'],C['shoe'],C['hair'])
skinM,clothM,shoeM,hairM=[clay('c%d'%j,c) for j,c in enumerate(V['col'])];ink=clay('ink','#3a2c2a');white=clay('wh','#ffffff');pink=clay('pk','#ff9f9f')
h=.0075;lo=np.array([-.62,-.6,-.03]);hi=np.array([.62,.62,1.22]);G=np.stack(np.meshgrid(*[np.arange(lo[i],hi[i],h) for i in range(3)],indexing='ij'),-1)
def build(name,parts,k,mat,cut=None,extra=None):
    if not parts and not extra:return
    d=sdf(G,parts,k) if parts else np.full(G.shape[:-1],1.0,np.float32)
    if cut:d=np.maximum(d,-sdf(G,cut,0))
    if extra:d1=sdf(G,extra,k);hh=np.clip(.5+.5*(d-d1)/.02,0,1);d=d*(1-hh)+d1*hh-.02*hh*(1-hh)
    v,f,_,_=measure.marching_cubes(d,0,spacing=(h,h,h));o=mk(name,v+lo,[tuple(int(i) for i in t[::-1]) for t in f],mat);m=o.modifiers.new('sm','SMOOTH');m.factor=.5;m.iterations=3
build('skin',V['skin'],.04,skinM);build('ears',V['ears'],0,skinM);build('arm',ARM,0,clothM);build('hand',HAND,0,skinM);pantsM=clay('pants',V['C']['pants'] if 'C' in V else ('#6f8fc0' if VI==4 else '#59607a'));PT=V.get('pt','shorts')
if PT=='long':LEG=[(c,r*np.array([1.18,1.18,1]),Rm,p) for c,r,Rm,p in LEG]
if PT=='longskirt':LEG=[]
build('leg',LEG,0,pantsM if PT=='long' else (skinM if VI in (2,4,5,7) else pantsM));
if V.get('hat'):build('hat',V['hat'],.02,clay('hat',V['C'].get('hat','#888888')),V['hatcut'],V['hatx'])
build('pants',V['pants'],.02,pantsM,V['pantscut']);build('cloth',V['cloth'],.035,clothM,V['clothcut']);build('shoe',V['shoe'],.02,shoeM);build('hair',V['hair'],.03,hairM,V['cut'],V['hairx'])
# face seated on the sculpted head surface
HP=[V['skin'][0]]+[p for p in V['skin'][1:] if p[1].max()>.09];Hc=np.array([0,0,V['hz']])
def surf(d):
    d=np.array(d,float);d/=np.linalg.norm(d);ts=np.arange(0,.7,.002);pts=Hc[None]+ts[:,None]*d[None];vals=sdf(pts,HP,.04);p=pts[np.where(vals<0)[0].max()];ee=.005
    n=np.array([sdf((p+a*ee)[None],HP,.04)[0]-sdf((p-a*ee)[None],HP,.04)[0] for a in np.eye(3)]);return Vector(p),Vector(n).normalized()
SV=[];SF=[];nu,nv=20,12
for i in range(nv+1):
    for j in range(nu):a=i/nv*pi;b=j/nu*2*pi;SV.append((sin(a)*cos(b),sin(a)*sin(b),cos(a)))
for i in range(nv):
    for j in range(nu):SF.append((i*nu+j,(i+1)*nu+j,(i+1)*nu+(j+1)%nu,i*nu+(j+1)%nu))
def feat(d,size,mat,lift=.3,roll=0):
    p,n=surf(d);up=Vector((0,0,1));up=(up-n*up.dot(n)).normalized();rt=up.cross(n).normalized();r2=rt*cos(roll)+up*sin(roll);u2=up*cos(roll)-rt*sin(roll);c=p+n*size[1]*lift;Mx=Matrix((r2*size[0],n*size[1],u2*size[2])).transposed();mk('f',[c+Mx@Vector(s) for s in SV],SF,mat,sub=1)
ex,ez=V['eye']
for s in (1,-1):
    feat((s*ex,-1,ez),(.03,.012,.04),ink,.2);feat((s*ex-.03,-1,ez+.055),(.01,.005,.01),white,1.6);feat((s*(ex+.3),-1,ez-.16),(.042,.006,.026),pink,.2)
    feat((s*.03,-1,ez-.2),(.022,.006,.006),ink,.3,roll=s*.5)
if os.environ.get('EXPORT'):
    import json,base64
    TGT=dict(skin=520,hair=700,hat=360,cloth=220,pants=160,ears=60,arm=60,hand=50,leg=60,shoe=70,f=28)
    dg=bpy.context.evaluated_depsgraph_get();parts={}
    def piv_arm(a):c,r,Rm,p=a;return c+Rm@np.array([0,0,r[2]])
    PIV={'body':np.zeros(3)}
    for a in ARM:PIV['armL' if a[0][0]>0 else 'armR']=piv_arm(a)
    for a in LEG:PIV['legL' if a[0][0]>0 else 'legR']=a[0]+np.array([0,0,a[1][2]])
    if 'legL' not in PIV:PIV['legL']=np.array([.05,0,.11]);PIV['legR']=np.array([-.05,0,.11])
    for o in list(bpy.data.objects):
        if o.type!='MESH':continue
        base=o.name.split('.')[0];tg=TGT.get(base)
        if tg is None:continue
        nt=len(o.data.polygons)*(2 if base=='f' else 1)
        if base!='f':nt=sum(len(p.vertices)-2 for p in o.data.polygons)
        else:nt=len(o.data.polygons)*2*4
        if nt>tg*1.2:
            d=o.modifiers.new('dec','DECIMATE');d.ratio=max(.002,tg/nt)
        dg.update();oe=o.evaluated_get(dg);me=oe.to_mesh();me.calc_loop_triangles()
        col=o.data.materials[0]['hex'];rgb=[int(col[i:i+2],16) for i in (1,3,5)]
        V=np.array([v.co for v in me.vertices]);Nn=np.array([v.normal for v in me.vertices]);T=np.array([t.vertices for t in me.loop_triangles])
        oe.to_mesh_clear()
        if len(T)==0:continue
        A,B_,C_=V[T[:,0]],V[T[:,1]],V[T[:,2]];vol=(A*np.cross(B_,C_)).sum()
        if vol<0:T=T[:,::-1].copy();Nn=-Nn
        cx=V[T].mean(1)[:,0]
        def side(name):
            return name+('L' if 1 else '')
        groups=[]
        if base in('arm','hand'):groups=[('armL',cx>0),('armR',cx<=0)]
        elif base in('leg','shoe'):groups=[('legL',cx>0),('legR',cx<=0)]
        else:groups=[('body',np.ones(len(T),bool))]
        for g,mask in groups:
            TT=T[mask]
            if not len(TT):continue
            used=np.unique(TT);remap=-np.ones(len(V),int);remap[used]=np.arange(len(used))
            P=parts.setdefault(g,dict(V=[],N=[],C=[],I=[],n=0))
            P['I'].append(remap[TT]+P['n']);P['V'].append(V[used]);P['N'].append(Nn[used]);P['C'].append(np.tile(rgb,(len(used),1)));P['n']+=len(used)
    out={};tot=0
    for g,P in parts.items():
        V=np.concatenate(P['V'])-PIV[g];Nn=np.concatenate(P['N']);C=np.concatenate(P['C']).astype(np.uint8);I=np.concatenate(P['I']).astype(np.uint16)
        V=V[:,[0,2,1]]*np.array([1,1,-1]);Nn=Nn[:,[0,2,1]]*np.array([1,1,-1]);pv=PIV[g][[0,2,1]]*np.array([1,1,-1])
        q=np.clip(np.round(V*16384),-32767,32767).astype(np.int16);nq=np.clip(np.round(Nn*127),-127,127).astype(np.int8)
        b=lambda a:base64.b64encode(a.tobytes()).decode()
        out[g]=dict(p=b(q),n=b(nq),c=b(C),i=b(I),piv=[round(float(x),4) for x in pv]);tot+=len(I)
    json.dump(out,open(os.environ['EXPORT'],'w'));print('TRIS',tot,{g:len(np.concatenate(P['I'])) for g,P in parts.items()});raise SystemExit
fl=mk('floor',[(-6,-6,0),(6,-6,0),(6,6,0),(-6,6,0)],[(0,1,2,3)],white);fl.is_shadow_catcher=True
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.9,.88,.92,1);w.node_tree.nodes['Background'].inputs[1].default_value=.6
def light(loc,en,size,c=(1,1,1)):
    l=bpy.data.lights.new('l','AREA');l.energy=en;l.size=size;l.color=c;o=bpy.data.objects.new('L',l);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.5))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
light((-2.2,-2.6,3.0),95,2.5,(1,.97,.92));light((2.6,-1.8,1.2),16,3,(.92,.94,1));light((.6,2.6,2.2),30,2)
cam=bpy.data.cameras.new('cam');cam.type='ORTHO';co=bpy.data.objects.new('cam',cam);col.objects.link(co);sc.camera=co;ang=float(os.environ.get('ANG','-.3'));el=.13;d=Vector((sin(ang)*cos(el),-cos(ang)*cos(el),sin(el)));co.location=Vector((0,0,.55))+d*8;co.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=1.5
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=40;sc.cycles.use_denoising=True;sc.view_settings.view_transform='Standard';sc.render.film_transparent=True;sc.render.resolution_x=sc.render.resolution_y=int(os.environ.get('RES','440'));sc.render.filepath=os.path.join(OUT,'p_%02d%s.png'%(VI,os.environ.get('TAG','')));bpy.ops.render.render(write_still=True)
