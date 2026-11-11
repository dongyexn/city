# CGTrader 'Sunny Lazy Bear'(free) 메시를 바탕으로 사람 주민으로 각색 → 템플릿 규칙(ARM_L…)의 .blend
import bpy,bmesh,sys,math,os,numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector,Matrix
SRC,OUT=sys.argv[-2],sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=SRC);dg=bpy.context.evaluated_depsgraph_get()
def baked(n,dec=None):
    o=bpy.data.objects[n]
    if dec:
        d=o.modifiers.new('__d','DECIMATE');d.ratio=dec;dg.update()
    me=bpy.data.meshes.new_from_object(o.evaluated_get(dg));me.transform(o.matrix_world);bm=bmesh.new();bm.from_mesh(me);bpy.data.meshes.remove(me);return bm
B={k:baked(k,d) for k,d in [('Cubo',.3),('cuerpo',.2),('brazos',None),('guantes',None),('ojo',None),('ojo.001',None),('blanco',None),('blanco.001',None),('pupila',None),('pupila.001',None),('brillo',None),('brillo.001',None),('boca',None)]}
# wipe source scene
HB=BVHTree.FromBMesh(B['Cubo'])
def onface(x,z):
    h=HB.ray_cast(Vector((x,-3,z)),Vector((0,1,0)));return h[0],h[1]
def blob(b,c,r,n=None):
    t=bmesh.new();bmesh.ops.create_uvsphere(t,u_segments=16,v_segments=10,radius=1);M=Matrix.Translation(c)
    if n is not None:M=M@n.to_track_quat('Y','Z').to_matrix().to_4x4()
    bmesh.ops.transform(t,matrix=M@Matrix.Diagonal((r[0],r[2] if n is None else r[1],r[1] if n is None else r[2],1)),verts=t.verts)
    me=bpy.data.meshes.new('t');t.to_mesh(me);t.free();b.from_mesh(me);bpy.data.meshes.remove(me)
def feat(b,x,z,rx,rz,d=.025,lift=0):
    p,n=onface(x,z);blob(b,p+n*lift,(rx,d,rz),-n)
def arc(b,x0,z0,w,h,r,k=9,lift=.005):
    for i in range(k):
        a=math.pi*i/(k-1);feat(b,x0-w*math.cos(a),z0-h*math.sin(a),r,r,r*.6,lift)
def face(col,style,INK,WH,PK,mkf):
    ink=bmesh.new();wh=bmesh.new();pk=bmesh.new();EZ=1.93;EX=.36
    if style=='dot':
        for sg in (1,-1):feat(ink,sg*EX,EZ,.085,.11);feat(wh,sg*EX-.03,EZ+.045,.028,.028,.02,.02)
        arc(ink,0,1.775,.07,.035,.018)
    elif style=='happy':
        for sg in (1,-1):arc(ink,sg*EX,EZ-.04,.1,-.07,.024)
        arc(ink,0,1.76,.09,.05,.02)
    elif style=='bean':
        for sg in (1,-1):feat(ink,sg*EX,EZ,.06,.095);feat(wh,sg*EX-.02,EZ+.04,.02,.02,.02,.02)
        feat(ink,0,1.77,.04,.022)
    elif style=='sleepy':
        for sg in (1,-1):arc(ink,sg*EX,EZ,.085,.03,.02,7)
        arc(ink,0,1.78,.06,.03,.018,7)
    for sg in (1,-1):feat(pk,sg*.62,1.80,.13,.07,.02)
    mkf(ink,'FACE_eyes',INK);mkf(wh,'FACE_highlight',WH) if wh.verts else wh.free();mkf(pk,'FACE_blush',PK)
for o in list(bpy.data.objects):bpy.data.objects.remove(o)
for c in list(bpy.data.collections):bpy.data.collections.remove(c)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
for i in list(bpy.data.images):bpy.data.images.remove(i)
S=.95/3.337;Z0=.015
HC=np.array([-.027,-.01,2.278]);HH=np.array([1.236,1.062,1.059])
def copy(bm,keep=None,nz=(-2,2)):
    b=bm.copy()
    if keep or nz!=(-2,2):
        b.normal_update();keep=keep or (lambda c:True)
        bmesh.ops.delete(b,geom=[f for f in b.faces if not (keep(f.calc_center_median()) and nz[0]<=f.normal.z<=nz[1])],context='FACES')
        bmesh.ops.delete(b,geom=[v for v in b.verts if not v.link_faces],context='VERTS')
    return b
def push(b,d):
    b.normal_update()
    for v in b.verts:v.co+=v.normal*d
    return b
def cap(b):
    e=[e for e in b.edges if e.is_boundary]
    if e:bmesh.ops.holes_fill(b,edges=e,sides=0)
    return b
MATS={}
def mat(name,hexc):
    k=name+hexc
    if k in MATS:return MATS[k]
    m=bpy.data.materials.new(name);c=[(int(hexc[i:i+2],16)/255) for i in (1,3,5)];c=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c]+[1]
    m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=c;b.inputs['Roughness'].default_value=.8;m.diffuse_color=c;MATS[k]=m;return m
def mk(col,b,name,m,parent=None,piv=None,solid=0,it=12):
    bmesh.ops.transform(b,matrix=Matrix.Translation((0,0,-Z0*S))@Matrix.Diagonal((S,S,S,1)),verts=b.verts)
    me=bpy.data.meshes.new(name);b.to_mesh(me);b.free();me.materials.append(m);me.polygons.foreach_set('use_smooth',[True]*len(me.polygons))
    o=bpy.data.objects.new(name,me);col.objects.link(o)
    if piv is not None:
        p=Vector(((piv[0])*S,piv[1]*S,(piv[2]-Z0)*S));me.transform(Matrix.Translation(-p));o.location=p
    if parent:me.transform(Matrix.Translation(-parent.location));o.parent=parent;o.location=(0,0,0)
    if solid:
        m=o.modifiers.new('다듬기','SMOOTH');m.factor=1.0;m.iterations=it
        s=o.modifiers.new('두께','SOLIDIFY');s.thickness=solid;s.offset=-1
    return o
hn=lambda p:(np.array(p)-HC)/HH
def hairmask(style):
    def keep(p):
        x,y,z=hn(p);bang=.2+.05*math.sin(x*14)
        if y<-.25 and z<bang:return False
        if style=='short':return z>-.2 or (y>.35 and z>-.55)
        if style=='buzz':return z>.05 or (y>.4 and z>-.3)
        if style=='bob':return z>-.62 and not (y<-.25 and abs(x)<.7 and z<bang)
        if style=='cap':return z>-.15
        return True
    return keep
# arm / leg split helpers
ARM=B['brazos'];GLV=B['guantes'];BODY=B['cuerpo'];CR=.22
def vox(b,size):
    me=bpy.data.meshes.new('v');b.to_mesh(me);b.free();o=bpy.data.objects.new('v',me);bpy.context.scene.collection.objects.link(o)
    me.remesh_voxel_size=size
    with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o]):bpy.ops.object.voxel_remesh()
    r=bmesh.new();r.from_mesh(o.data);bpy.data.objects.remove(o);bpy.data.meshes.remove(me);return r
def lower(z0,z1,d):
    b=cap(push(copy(BODY,lambda c:c.z<z1+.08),d));r=vox(b,.016)
    bmesh.ops.delete(r,geom=[f for f in r.faces if not (z0<f.calc_center_median().z<z1)],context='FACES');bmesh.ops.delete(r,geom=[v for v in r.verts if not v.link_faces],context='VERTS');return r
def side(b,sg):return copy(b,lambda c:(c.x>0)==(sg>0))
V=[(1,'L'),(-1,'R')]
APIV={sg:np.array([sg*.36,0,1.13]) for sg,_ in V};LPIV={sg:np.array([sg*.27,0,CR]) for sg,_ in V}
VAR=[ # hair style, hair, shirt, pants, shoe, skin, pants kind, hat, extra
 dict(h='short',hc='#3b2a24',top='#f2c14e',bot='#6f8fc0',sh='#3f4a6b',sk='#ffd9c0',pk='shorts'),
 dict(h='cap',hc='#5a3a26',top='#f7f4ee',bot='#c9b48a',sh='#5a4636',sk='#f3c6a4',pk='long',hat='#3f6fb5'),
 dict(h='bob',hc='#7a4a32',top='#f4a7b4',bot='#f4a7b4',sh='#c0607a',sk='#ffe6d6',pk='dress'),
 dict(h='bob',hc='#c2733e',top='#b79be0',bot='#5a4a8a',sh='#4a3a6a',sk='#ffd9c0',pk='shorts',bun=1),
 dict(h='short',hc='#cfcac6',top='#d8c3a5',bot='#6a5040',sh='#3a2a24',sk='#ffe6d6',pk='long'),
 dict(h='buzz',hc='#1f1a18',top='#f7f4ee',bot='#3a3a40',sh='#e8e4dc',sk='#c98d68',pk='shorts'),
 dict(h='bob',hc='#2b2422',top='#9fd8d0',bot='#5f7fb0',sh='#f2f0ea',sk='#ffd9c0',pk='long'),
 dict(h='cap',hc='#2a201c',top='#f39a4a',bot='#2f5f8a',sh='#3a3a3a',sk='#d9a27c',pk='shorts',hat='#e05a4a'),
]
for k,v in enumerate(VAR):
    col=bpy.data.collections.new('주민_%02d'%(k+1));bpy.context.scene.collection.children.link(col)
    SK=mat('피부',v['sk']);TOP=mat('상의',v['top']);BOT=mat('하의',v['bot']);SH=mat('신발',v['sh']);HR=mat('머리카락',v['hc']);INK=mat('눈','#2e2624');WH=mat('눈_하이라이트','#ffffff');PK=mat('볼터치','#ff9f9f')
    mk(col,copy(B['Cubo']),'HEAD',SK)
    face(col,os.environ.get('FACE') or v.get('face','dot'),INK,WH,PK,lambda b,n,m:mk(col,b,n,m))
    if v['h'] in ('short','buzz','cap'):
        for sg in (1,-1):
            b=bmesh.new();bmesh.ops.create_uvsphere(b,u_segments=20,v_segments=12,radius=1);bmesh.ops.transform(b,matrix=Matrix.Translation((sg*1.2,.05,1.98))@Matrix.Diagonal((.14,.2,.24,1)),verts=b.verts);mk(col,b,'HEAD_EAR',SK)
    hb=push(copy(B['Cubo'],hairmask(v['h'])),.05 if v['h']!='buzz' else .025);mk(col,hb,'HAIR',HR,solid=.012 if v['h']!='buzz' else .006)
    if v.get('bun'):
        for sg in (1,-1):
            b=bmesh.new();bmesh.ops.create_uvsphere(b,u_segments=20,v_segments=12,radius=1);bmesh.ops.transform(b,matrix=Matrix.Translation((sg*.95,.25,3.05))@Matrix.Diagonal((.32,.3,.3,1)),verts=b.verts);mk(col,b,'HAIR_bun',HR)
    if v.get('hat'):
        HT=mat('모자',v['hat']);mk(col,push(copy(B['Cubo'],lambda c:hn(c)[2]>.12),.11),'HAT',HT,solid=.014)
        b=bmesh.new();bmesh.ops.create_uvsphere(b,u_segments=24,v_segments=12,radius=1);bmesh.ops.transform(b,matrix=Matrix.Translation((0,-1.0,HC[2]+.12*HH[2]))@Matrix.Diagonal((.95,.55,.06,1)),verts=b.verts);mk(col,b,'HAT_brim',HT)
    # body: skin core, legs split off below the crotch
    mk(col,cap(copy(BODY,lambda c:c.z>=CR)),'BODY',SK)
    wz=.58 if v['pk']!='dress' else .1
    mk(col,push(copy(BODY,lambda c:c.z>wz-.04 and c.z<1.25),.06),'SHIRT',TOP,solid=.01)
    PL=None
    if v['pk']=='dress':
        b=bmesh.new();PR=[(.6,.6),(.5,.66),(.38,.71),(.26,.75),(.17,.77),(.13,.76)];ns=40
        for z,rr in PR:
            for j in range(ns):a=j/ns*2*math.pi;b.verts.new((math.cos(a)*rr,.05+math.sin(a)*rr*.85,z))
        b.verts.ensure_lookup_table()
        for k2 in range(len(PR)-1):
            for j in range(ns):b.faces.new([b.verts[k2*ns+j],b.verts[k2*ns+(j+1)%ns],b.verts[(k2+1)*ns+(j+1)%ns],b.verts[(k2+1)*ns+j]])
        bmesh.ops.recalc_face_normals(b,faces=b.faces[:]);o=mk(col,b,'SHIRT_skirt',TOP,solid=.01,it=0);s2=o.modifiers.new('곡면','SUBSURF');s2.levels=2;s2.render_levels=2
    else:
        PL=lower(.08 if v['pk']=='long' else .14,.62,.045)
        mk(col,copy(PL,lambda c:c.z>=CR+.02),'PANTS',BOT,solid=.01,it=3)
    arms={};legs={}
    for sg,t in V:
        a=mk(col,side(ARM,sg),'ARM_'+t,SK,piv=APIV[sg]);arms[sg]=a
        mk(col,side(GLV,sg),'ARM_'+t+'_HAND',SK,parent=a)
        mk(col,push(side(copy(ARM,lambda c:np.linalg.norm(np.array(c)-APIV[1 if c.x>0 else -1])<.45),sg),.03),'ARM_'+t+'_SLEEVE',TOP,parent=a,solid=.008,it=2)
        l=mk(col,cap(side(copy(BODY,lambda c:c.z<CR+.01),sg)),'LEG_'+t,SK,piv=LPIV[sg]);legs[sg]=l
        mk(col,push(side(copy(BODY,lambda c:c.z<.09,nz=(-2,.6)),sg),.035),'LEG_'+t+'_SHOE',SH,parent=l,solid=.012,it=2)
        if PL is not None:
            mk(col,side(copy(PL,lambda c:c.z<CR+.02),sg),'LEG_'+t+'_PANTS',BOT,parent=l,solid=.01,it=2)
    for o in col.objects:
        if o.parent is None:o.location.x+=k*1.0
me=bpy.data.meshes.new('GUIDE_FLOOR');me.from_pydata([(-.6,-.6,0),(len(VAR)-.4,-.6,0),(len(VAR)-.4,.6,0),(-.6,.6,0)],[],[(0,1,2,3)])
g=bpy.data.objects.new('GUIDE_FLOOR',me);bpy.context.scene.collection.objects.link(g);g.display_type='WIRE';g.hide_select=True;g.hide_render=True
t=bpy.data.texts.new('README');t.write("""ISLE 주민 템플릿 (바탕 메시: CGTrader 'Sunny Lazy Bear' 무료 모델을 사람으로 각색)
- 컬렉션 하나 = 주민 한 명. 정면 -Y, 바닥 Z 0, 키 약 0.95 유지.
- ARM_L/ARM_R/LEG_L/LEG_R 로 시작하는 오브젝트만 걸을 때 흔들림. 관절 = 그 네 오브젝트의 원점.
- 옷(SHIRT, PANTS, SLEEVE…)은 몸(BODY, ARM, LEG) 위에 띄운 껍질 + '두께' 모디파이어. 두께·띄움은 자유롭게 수정 가능.
- 색은 머티리얼 Base Color만. GUIDE 로 시작하거나 렌더에서 숨긴 오브젝트는 무시.
""")
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=True);print('SAVED',OUT)
