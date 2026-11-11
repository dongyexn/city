# .blend(주민 템플릿 규칙) → 게임용 ppl.json
# 사용: bpy가 설치된 파이썬으로  python import_people.py 입력.blend [입력2.blend …] 출력.json
import bpy,bmesh,sys,json,base64,numpy as np
args=sys.argv[1:];ins,out=args[:-1],args[-1];BUDGET=3600
def srgb(c):return [int(round(255*(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055))) for v in c[:3]]
def color(m):
    if m is None:return [200,200,200]
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type=='BSDF_PRINCIPLED':return srgb([max(0,min(1,v)) for v in n.inputs['Base Color'].default_value])
    return srgb(m.diffuse_color)
def grp(name):
    b=name.split('.')[0].upper()
    for j,g in (('ARM_L','armL'),('ARM_R','armR'),('LEG_L','legL'),('LEG_R','legR')):
        if b==j or b.startswith(j+'_'):return g
    return 'body'
chars=[]
for f in ins:
    bpy.ops.wm.open_mainfile(filepath=f)
    for col in sorted(bpy.data.collections,key=lambda c:c.name):
        obs=[o for o in col.objects if o.type=='MESH' and not o.name.upper().startswith('GUIDE') and not o.hide_render]
        if not obs:continue
        dg=bpy.context.evaluated_depsgraph_get()
        tris=lambda o:sum(len(p.vertices)-2 for p in o.evaluated_get(dg).data.polygons)
        tc={o.name:tris(o) for o in obs};tot=sum(tc.values())
        if tot>BUDGET:
            w={k:v**.6 for k,v in tc.items()};sw=sum(w.values())
            for o in obs:
                tgt=max(40,BUDGET*w[o.name]/sw)
                if tc[o.name]>tgt:d=o.modifiers.new('__dec','DECIMATE');d.ratio=tgt/tc[o.name]
            dg=bpy.context.evaluated_depsgraph_get();dg.update()
        piv={}
        for j,g in (('ARM_L','armL'),('ARM_R','armR'),('LEG_L','legL'),('LEG_R','legR')):
            o=col.objects.get(j)
            if o:piv[g]=np.array(o.matrix_world.translation)
        P={}
        for o in obs:
            g=grp(o.name);oe=o.evaluated_get(dg);me=oe.to_mesh();me.calc_loop_triangles();Mw=np.array(o.matrix_world);Nm=np.linalg.inv(Mw[:3,:3]).T
            V=np.array([v.co for v in me.vertices]);V=V@Mw[:3,:3].T+Mw[:3,3];Nn=np.array([v.normal for v in me.vertices])@Nm.T;Nn/=np.linalg.norm(Nn,axis=1,keepdims=True)+1e-9
            cols=[color(s.material) for s in o.material_slots] or [color(None)]
            D=P.setdefault(g,dict(V=[],N=[],C=[],I=[],key={}))
            for t in me.loop_triangles:
                mi=min(t.material_index,len(cols)-1);ids=[]
                for vi in t.vertices:
                    k=(o.name,vi,mi)
                    if k not in D['key']:D['key'][k]=len(D['V']);D['V'].append(V[vi]);D['N'].append(Nn[vi]);D['C'].append(cols[mi])
                    ids.append(D['key'][k])
                D['I'].append(ids)
            oe.to_mesh_clear()
        if 'body' not in P:continue
        allV=np.array(P['body']['V']);cx,cy=((piv['armL'][:2]+piv['armR'][:2])/2) if 'armL' in piv and 'armR' in piv else (allV[:,:2].min(0)+allV[:,:2].max(0))/2
        for g in P:
            if g not in piv:pts=np.array(P[g]['V']);piv[g]=np.array([pts[:,0].mean(),pts[:,1].mean(),pts[:,2].max()]) if g!='body' else np.array([cx,cy,0])
        piv['body']=np.array([cx,cy,0])
        ch={};b64=lambda a:base64.b64encode(a.tobytes()).decode();T=lambda a:a[:,[0,2,1]]*np.array([1,1,-1]);n=0
        for g,D in P.items():
            pv=piv[g];V=T(np.array(D['V'])-pv);Nn=T(np.array(D['N']));C=np.array(D['C'],np.uint8);I=np.array(D['I'],np.uint16).reshape(-1)
            pvo=T((pv-np.array([cx,cy,0]))[None])[0]
            ch[g]=dict(p=b64(np.clip(np.round(V*16384),-32767,32767).astype(np.int16)),n=b64(np.clip(np.round(Nn*127),-127,127).astype(np.int8)),c=b64(C),i=b64(I),piv=[round(float(x),4) for x in pvo]);n+=len(I)//3
        for g in ('armL','armR','legL','legR'):
            if g not in ch:ch[g]=dict(p='',n='',c='',i='',piv=[0,0,0])
        chars.append(ch);print('주민',col.name,'삼각형',n)
json.dump({str(i+1):c for i,c in enumerate(chars)},open(out,'w'),separators=(',',':'));print('saved',out,len(chars))
