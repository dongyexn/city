# 베이스 메시 → 블렌더: 클레이 재질, 뼈대·가중치, 턴어라운드·포즈 렌더, GLB
import os, sys, math, numpy as np
D0 = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D0)
import chibi15 as C
import bpy, bmesh
from mathutils import Vector, Matrix

JOBS = os.environ.get('JOBS', 'turn').split(',')
RES = int(os.environ.get('RES', 420)); SAMP = int(os.environ.get('SAMP', 20))
OUT = os.path.join(D0, os.environ.get('OUTD', 'out')); os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
def node(nt, t): return next(n for n in nt.nodes if n.type == t)
def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = node(m.node_tree, 'BSDF_PRINCIPLED'); b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    return m
def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)
SKIN = mat('clay_skin', srgb('#e4b491'), 0.8)          # 이전 SD 캐릭터와 같은 살구색, 거칠기는 앱 주민 값(.8)
# 얼굴 재질: 이전에 만든 얼굴(동글눈)과 같은 색
INK = mat('ink', srgb('#2b211e'), 0.32); WHITE = mat('white', (1, 1, 1), 0.25); CHEEK = mat('cheek', srgb('#f29a8e'), 0.75); MOUTH = mat('mouth', srgb('#8a3b33'), 0.5)
_wb = node(WHITE.node_tree, 'BSDF_PRINCIPLED'); _wb.inputs['Emission Color'].default_value = (1, 1, 1, 1); _wb.inputs['Emission Strength'].default_value = 0.6

# ------------------------------------------------------------------ 메시
d = np.load(os.path.join(D0, os.environ.get('MESH', 'mesh.npz'))); V, F = d['v'], d['f']
def outward(v, f):          # 면이 바깥을 보도록(부피가 음수면 뒤집힌 것)
    return f if np.einsum('ij,ij->i', v[f[:, 0]], np.cross(v[f[:, 1]], v[f[:, 2]])).sum() > 0 else f[:, ::-1].copy()
F = outward(V, F)
me = bpy.data.meshes.new('Base15'); me.from_pydata(V.tolist(), [], F.tolist()); me.update()
for p in me.polygons: p.use_smooth = True
body = bpy.data.objects.new('Base15', me); sc.collection.objects.link(body); me.materials.append(SKIN)

# ------------------------------------------------------------------ 얼굴: 이전 SD 캐릭터의 얼굴(동글눈 A) 구성을 새 머리 치수로 옮김
# 눈(먹색 점토 방울 + 흰 하이라이트) · 눈썹 · 볼터치 · 웃는 입. 전부 머리 표면을 따라 붙는다.
def face_parts():
    obs = []
    def dome(name, cx, cz, rx, rz, h, m, base=-0.002, rings=7, seg=28):
        """표면에 붙는 타원 점토 방울: 가장자리는 표면 속(base), 가운데로 h만큼 솟음"""
        vs, fs = [], []
        def pt(x, z, rho): return (x, C.surf_y(x, z) - (base + h * math.sqrt(max(0.0, 1 - rho * rho))), z)
        vs.append(pt(cx, cz, 0))
        for r in range(1, rings + 1):
            for k in range(seg):
                a = 2 * math.pi * k / seg; vs.append(pt(cx + rx * r / rings * math.cos(a), cz + rz * r / rings * math.sin(a), r / rings))
        for k in range(seg): fs.append((0, 1 + (k + 1) % seg, 1 + k))
        for r in range(1, rings):
            o0, o1 = 1 + (r - 1) * seg, 1 + r * seg
            for k in range(seg): fs.append((o0 + k, o0 + (k + 1) % seg, o1 + (k + 1) % seg, o1 + k))
        dm = bpy.data.meshes.new(name); dm.from_pydata(vs, [], fs); dm.update()
        for p in dm.polygons: p.use_smooth = True
        o = bpy.data.objects.new(name, dm); sc.collection.objects.link(o); dm.materials.append(m); return o
    def stroke(name, path, w, m):
        """점토를 굴린 줄(눈썹·입): 표면을 따라가고 양 끝은 가늘어짐"""
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = w; cu.bevel_resolution = 4; cu.use_fill_caps = True
        sp = cu.splines.new('POLY'); sp.points.add(len(path) - 1); n = len(path)
        for i, (p, (x, z)) in enumerate(zip(sp.points, path)):
            p.co = (x, C.surf_y(x, z) - 0.0005, z, 1)
            e = min(i, n - 1 - i) / 3.0; p.radius = max(math.sqrt(min(1.0, e)), 0.35)
        o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); cu.materials.append(m); return o
    EX, EZ = C.EYE_X, C.EYE_Z; Q = C.Q
    for sx in (-1, 1):
        x = sx * EX
        obs.append(dome(f'Eye{sx}', x, EZ, Q['eyeW'], Q['eyeH'], 0.0175, INK))
        obs.append(dome(f'EyeHi{sx}', x - 0.34 * Q['eyeW'], EZ + 0.40 * Q['eyeH'], 0.38 * Q['eyeW'], 0.38 * Q['eyeH'], 0.003, WHITE, base=0.0135, rings=4, seg=18))
        bz = EZ + Q['browDZ']                                           # 눈썹: 눈 위, 가운데가 살짝 볼록
        obs.append(stroke(f'Brow{sx}', [(x + sx * t * Q['browLen'], bz + 0.0065 * (1 - t * t) + Q['browTilt'] * t) for t in np.linspace(-1, 1, 13)], 0.0083, INK))
        obs.append(dome(f'Cheek{sx}', sx * (EX + Q['blushDX']), EZ + Q['blushDZ'], Q['blushW'], Q['blushW'] * 0.643, 0.006, CHEEK, rings=6, seg=24))
    my = C.MOUTH_Z + 0.022                                        # 웃는 입: 아래로 볼록한 호(200°~340°)
    obs.append(stroke('Mouth', [(math.cos(a) * Q['mouthW'], my + math.sin(a) * Q['mouthCurve']) for a in np.linspace(math.radians(200), math.radians(340), 15)], 0.0062, MOUTH))
    return obs
FACE = face_parts()

# ------------------------------------------------------------------ 임시 헤어(있으면): 뒤통수 크기 판단용
HAIROB = None
def hair_mat(col):
    """클레이 헤어: 흐름 방향으로 길게 이어지는 가는 결(UV의 U = 흐름을 가로지르는 좌표)을 요철과 옅은 명암으로"""
    m = mat('hair', srgb(col), 0.62); nt = m.node_tree; b = node(nt, 'BSDF_PRINCIPLED'); N = nt.nodes.new; Lk = nt.links.new
    uv = N('ShaderNodeUVMap'); sp = N('ShaderNodeSeparateXYZ'); Lk(uv.outputs['UV'], sp.inputs[0])
    def grain(freq, detail):
        mu = N('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = freq; Lk(sp.outputs['X'], mu.inputs[0])
        nz = N('ShaderNodeTexNoise'); nz.noise_dimensions = '1D'; nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = detail; Lk(mu.outputs[0], nz.inputs['W']); return nz
    g1 = grain(float(os.environ.get('GRAIN1', 0.55)), 1.0); g2 = grain(float(os.environ.get('GRAIN2', 1.9)), 2.0)
    mx = N('ShaderNodeMath'); mx.operation = 'ADD'; Lk(g1.outputs['Fac'], mx.inputs[0])
    m2 = N('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 0.45; Lk(g2.outputs['Fac'], m2.inputs[0]); Lk(m2.outputs[0], mx.inputs[1])
    bp = N('ShaderNodeBump'); bp.inputs['Strength'].default_value = float(os.environ.get('GRAINS', 0.55)); bp.inputs['Distance'].default_value = 0.006
    Lk(mx.outputs[0], bp.inputs['Height']); Lk(bp.outputs['Normal'], b.inputs['Normal'])
    c0 = srgb(col); rp = N('ShaderNodeMapRange'); rp.inputs['From Min'].default_value = 0.35; rp.inputs['From Max'].default_value = 1.05; rp.inputs['To Min'].default_value = 0.78; rp.inputs['To Max'].default_value = 1.22
    Lk(mx.outputs[0], rp.inputs['Value']); vm = N('ShaderNodeVectorMath'); vm.operation = 'SCALE'; vm.inputs[0].default_value = c0; Lk(rp.outputs[0], vm.inputs['Scale']); Lk(vm.outputs['Vector'], b.inputs['Base Color'])
    return m
if os.environ.get('HAIR'):
    hd = np.load(os.path.join(D0, os.environ['HAIR'])); hF = hd['f']; hf = outward(hd['v'], hF); hflip = hf is not hF; hm = bpy.data.meshes.new('Hair'); hm.from_pydata(hd['v'].tolist(), [], hf.tolist()); hm.update()
    for p in hm.polygons: p.use_smooth = True
    HAIROB = bpy.data.objects.new('Hair', hm); sc.collection.objects.link(HAIROB)
    if 'luv' in hd:
        ul = hm.uv_layers.new(name='UVMap'); ul.data.foreach_set('uv', (hd['luv'].reshape(-1, 3, 2)[:, ::-1] if hflip else hd['luv']).astype(np.float32).reshape(-1)); hm.materials.append(hair_mat(os.environ.get('HAIRCOL', '#4a3328')))
    else: hm.materials.append(mat('hair', srgb('#3b2a22'), 0.6))

# ------------------------------------------------------------------ 뼈대
SH, AD = Vector(C.SH), Vector(C.ADIR)
def mir(v, s): return Vector((v[0] * s, v[1], v[2]))
HZ = float(C.HIP[2])
BONES = [('hips', None, (0, 0.005, HZ), (0, 0.005, HZ + 0.08)), ('spine', 'hips', (0, 0.005, HZ + 0.08), (0, 0.010, 0.420)),
         ('chest', 'spine', (0, 0.010, 0.420), (0, 0.016, 0.495)), ('neck', 'chest', (0, 0.016, 0.495), (0, 0.018, 0.552)),
         ('head', 'neck', (0, 0.018, 0.552), (0, 0.018, 1.00))]
for s, sfx in ((1, 'L'), (-1, 'R')):
    BONES += [('shoulder.' + sfx, 'chest', mir((0.035, 0.012, 0.462), s), mir(SH, s)), ('upper_arm.' + sfx, 'shoulder.' + sfx, mir(SH, s), mir(SH + AD * C.EL, s)), ('forearm.' + sfx, 'upper_arm.' + sfx, mir(SH + AD * C.EL, s), mir(SH + AD * C.WR, s)),
              ('hand.' + sfx, 'forearm.' + sfx, mir(SH + AD * C.WR, s), mir(SH + AD * (C.HN + 0.055), s)),
              ('thigh.' + sfx, 'hips', mir(C.HIP, s), mir(C.KNEE, s)), ('shin.' + sfx, 'thigh.' + sfx, mir(C.KNEE, s), mir(C.ANK, s)),
              ('foot.' + sfx, 'shin.' + sfx, mir(C.ANK, s), mir(C.TOE, s))]
BONES = [(n, p, Vector(h) + Vector(C.BY), Vector(t) + Vector(C.BY)) for n, p, h, t in BONES]      # 몸을 앞뒤로 민 만큼 뼈도 같이
arm = bpy.data.armatures.new('Rig15'); rig = bpy.data.objects.new('Rig15', arm); sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='EDIT')
for name, par, h, t in BONES:
    b = arm.edit_bones.new(name); b.head = Vector(h); b.tail = Vector(t)
    if par: b.parent = arm.edit_bones[par]
bpy.ops.object.mode_set(mode='OBJECT')

# ------------------------------------------------------------------ 가중치: 부위 거리장의 부드러운 혼합(이음새가 넓게 풀림) + 부위 안에서는 축 방향으로 나눔
def weights(V):
    X, Y, Z = V[:, 0], V[:, 1], V[:, 2]; A = np.abs(X); P = C.parts(X, Y, Z)
    TAU = {'head': 0.007, 'arm': 0.007}        # 팔은 어깨 구(球)째로 돌고 몸통은 그대로 → 섞이는 폭을 좁게
    P.pop('_z', None); P.pop('_ka', None); P.pop('_core', None)
    m = {k: np.exp(-np.maximum(P[k], -0.05) / TAU.get(k, 0.016)) for k in P}
    tot = sum(m.values()); m = {k: v / tot for k, v in m.items()}
    W = {}
    def add(n, w): W[n] = W.get(n, 0) + w
    L = X >= 0
    # 머리·목: 목은 가슴→목→머리로 높이에 따라
    add('head', m['head'])
    tn = C.sstep(0.47, 0.515, Z); th = C.sstep(0.53, 0.575, Z)
    add('chest', m['neck'] * (1 - tn)); add('neck', m['neck'] * tn * (1 - th)); add('head', m['neck'] * th)
    # 몸통: 골반/허리/가슴
    a = C.sstep(C.HIP[2] + 0.022, C.HIP[2] + 0.112, Z); b = C.sstep(0.385, 0.455, Z)
    cl = 0.0 * A                       # 어깨(쇄골) 뼈: 팔을 들 때 어깨선이 같이 올라감
    add('hips', m['torso'] * (1 - a)); add('spine', m['torso'] * a * (1 - b)); add('chest', m['torso'] * b * (1 - cl))
    add('shoulder.L', m['torso'] * b * cl * L); add('shoulder.R', m['torso'] * b * cl * (~L))
    # 팔: 축 방향 거리 t로 위팔/아래팔/손
    t = (A - C.SH[0]) * C.ADIR[0] + (Y - C.SH[1]) * C.ADIR[1] + (Z - C.SH[2]) * C.ADIR[2]
    e = C.sstep(C.EL - 0.028, C.EL + 0.028, t); w = C.sstep(C.WR - 0.022, C.WR + 0.022, t)
    for sfx, sel in (('L', L), ('R', ~L)):
        add('upper_arm.' + sfx, m['arm'] * (1 - e) * sel); add('forearm.' + sfx, m['arm'] * e * (1 - w) * sel); add('hand.' + sfx, m['arm'] * w * sel)
    # 다리: 높이로 허벅지/정강이, 발은 발 부위
    k = C.sstep(C.KNEE[2] + 0.03, C.KNEE[2] - 0.03, Z)
    for sfx, sel in (('L', L), ('R', ~L)):
        add('thigh.' + sfx, m['leg'] * (1 - k) * sel); add('shin.' + sfx, m['leg'] * k * sel); add('foot.' + sfx, m['foot'] * sel)
    return W

W = weights(V)
for name, w in W.items():
    g = body.vertex_groups.new(name=name)
    idx = np.nonzero(w > 0.004)[0]
    for i, x in zip(idx.tolist(), w[idx].tolist()): g.add([i], x, 'REPLACE')
bpy.context.view_layer.objects.active = body; bpy.ops.object.vertex_group_normalize_all(lock_active=False)
md = body.modifiers.new('Armature', 'ARMATURE'); md.object = rig
bpy.context.view_layer.update()
for o in FACE + ([HAIROB] if HAIROB else []):           # 얼굴 파츠·헤어는 머리 뼈에
    mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'BONE'; o.parent_bone = 'head'
    bpy.context.view_layer.update(); o.matrix_world = mw
bpy.context.view_layer.update()

# ------------------------------------------------------------------ 포즈 도우미: 월드 축 기준 회전(부모부터)
def rot(bone, axis, deg):
    pb = rig.pose.bones[bone]; h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ pb.matrix
    bpy.context.view_layer.update()
def reset():
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
def mv(bone, v):
    pb = rig.pose.bones[bone]; pb.matrix = Matrix.Translation(Vector(v)) @ pb.matrix; bpy.context.view_layer.update()

POSES = {
    'walk': lambda: [rot('thigh.L', 'X', -30), rot('shin.L', 'X', 22), rot('thigh.R', 'X', 24), rot('shin.R', 'X', 30), rot('foot.R', 'X', 15),
                     rot('upper_arm.L', 'X', 32), rot('forearm.L', 'X', -18), rot('upper_arm.R', 'X', -32), rot('forearm.R', 'X', -30), rot('head', 'Z', 14), rot('spine', 'Z', -6)],
    'sit': lambda: [mv('hips', (0, 0, -0.13)), rot('thigh.L', 'X', -82), rot('thigh.R', 'X', -82), rot('shin.L', 'X', 78), rot('shin.R', 'X', 78),
                    rot('upper_arm.L', 'Y', 12), rot('upper_arm.R', 'Y', -12), rot('head', 'X', -6)],
    'wave_old': lambda: [rot('shoulder.L', 'Y', -24), rot('upper_arm.L', 'Y', -54), rot('forearm.L', 'Y', -38), rot('hand.L', 'Y', 20), rot('head', 'Y', -9), rot('chest', 'Y', -4),
                         rot('upper_arm.R', 'Y', -18)],
    # 팔 들기 규칙: 어깨가 먼저 올라가고, 위팔은 수평 조금 위까지만, 나머지는 팔꿈치를 접어 올리고, 머리는 반대쪽으로 기울여 자리를 내줌
    # 넨도로이드식 팔 들기: 어깨·몸통은 그대로 두고 팔만 어깨 구를 축으로 돈다. 위팔은 옆으로 수평 조금 위까지, 팔꿈치를 접어 아래팔을 세움
    'wave': lambda: [rot('upper_arm.L', 'Y', -50), rot('upper_arm.L', 'Z', -18), rot('forearm.L', 'Y', -62),
                     rot('head', 'Y', -9), rot('upper_arm.R', 'Y', -10)],
    'cheer': lambda: [rot('upper_arm.L', 'Y', -50), rot('upper_arm.L', 'Z', -18), rot('forearm.L', 'Y', -62),
                      rot('upper_arm.R', 'Y', 50), rot('upper_arm.R', 'Z', 18), rot('forearm.R', 'Y', 62), rot('head', 'X', -6)],
    'bow': lambda: [rot('spine', 'X', 14), rot('chest', 'X', 12), rot('neck', 'X', 8), rot('head', 'X', 16), rot('upper_arm.L', 'X', -30), rot('upper_arm.R', 'X', -30),
                    rot('forearm.L', 'X', -50), rot('forearm.R', 'X', -50)],
    'twist': lambda: [rot('spine', 'Z', 18), rot('chest', 'Z', 16), rot('head', 'Z', 34), rot('head', 'X', -8), rot('thigh.L', 'Y', 10), rot('thigh.R', 'Y', -10),
                      rot('upper_arm.L', 'Y', -30), rot('upper_arm.R', 'Y', 30)],
}

# ------------------------------------------------------------------ 조명·카메라
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = RES; sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = float(os.environ.get('EXPO', 0.45))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; node(w.node_tree, 'BACKGROUND').inputs[0].default_value = (0.82, 0.86, 0.92, 1); node(w.node_tree, 'BACKGROUND').inputs[1].default_value = 0.30
def light(name, loc, energy, size, col=(1, 1, 1)):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.size = size; l.color = col
    o = bpy.data.objects.new(name, l); sc.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.8)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o
KEY = light('key', (-2.2, -3.0, 3.4), 85, 2.5, (1, 0.97, 0.93)); light('fill', (3.0, -2.0, 1.2), 16, 3.0, (0.9, 0.95, 1)); light('rim', (1.5, 3.0, 2.8), 45, 2.0)
bpy.ops.mesh.primitive_plane_add(size=30); gp = bpy.context.object; gp.is_shadow_catcher = True
cd = bpy.data.cameras.new('cam'); cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam; cd.lens = 85

HAIR_ON = False
def shoot(tag, az, el, target=(0, 0, 0.77), dist=4.7, face=True):
    gp.hide_render = el < 0
    for o in FACE: o.hide_render = not face
    if HAIROB: HAIROB.hide_render = not HAIR_ON
    T = Vector(target); a, e = math.radians(az), math.radians(el)
    L = T + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.location = L; cam.rotation_euler = (T - L).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(OUT, tag + '.png'); bpy.ops.render.render(write_still=True); print('R', tag, flush=True)

if 'turn' in JOBS:      # 전신 턴어라운드(얼굴 파츠 없이 형태만)
    for tag, az, el in (('t_front', 0, 4), ('t_q', 35, 10), ('t_side', 90, 4), ('t_bq', 145, 10), ('t_back', 180, 4), ('t_top', 30, 48), ('t_low', 25, -22), ('t_game', 35, 32)):
        shoot(tag, az, el, face=False)
if 'head' in JOBS:      # 얼굴 굴곡: 여러 각도에서 형태만 + 눈·입 얹은 것
    HT = (0, 0, 0.98)
    for tag, az, el in (('h_front', 0, 3), ('h_q20', 20, 6), ('h_q45', 45, 6), ('h_q70', 70, 4), ('h_side', 90, 2), ('h_up', 30, -25), ('h_down', 30, 35)):
        shoot(tag, az, el, HT, 3.1, face=False); shoot(tag + '_f', az, el, HT, 3.1, face=True)
if 'sh' in JOBS:        # 어깨·목 이음부 확대
    for tag, az, el in (('s_front', 0, 6), ('s_q', 35, 12), ('s_side', 90, 6), ('s_bq', 145, 12), ('s_back', 180, 6)):
        shoot(tag, az, el, (0, 0, 0.42), 2.1, face=False)
    reset(); POSES['wave'](); shoot('s_wave', 0, 6, (0, 0, 0.45), 2.3, face=False); shoot('s_wave_b', 180, 6, (0, 0, 0.45), 2.3, face=False); shoot('s_wave_q', 40, 12, (0, 0, 0.45), 2.3, face=False); reset()
if 'arm' in JOBS:       # 팔 들기 비교: 기존(곧게 위로) / 규칙 적용 / 양팔
    for name in ('wave', 'cheer'):
        reset(); POSES[name](); shoot('a_' + name, 0, 6, (0, 0, 0.62), 3.6); shoot('a_' + name + '_q', 35, 12, (0, 0, 0.62), 3.6); shoot('a_' + name + '_b', 180, 6, (0, 0, 0.62), 3.6, face=False)
    reset()
if 'side' in JOBS:      # 몸 앞뒤 위치 비교용
    shoot('c_side', 90, 4); shoot('c_q', 35, 10); shoot('c_front', 0, 6, (0, 0, 0.36), 2.3, face=False)
if 'hair' in JOBS:      # 헤어를 얹은 모습과 맨머리 비교
    for on, sfx in ((False, ''), (True, '_h')):
        HAIR_ON = on and HAIROB is not None
        for tag, az, el in (('k_front', 0, 6), ('k_q', 35, 10), ('k_side', 90, 4), ('k_bq', 145, 10), ('k_back', 180, 6)):
            shoot(tag + sfx, az, el)
    HAIR_ON = False
if 'hairhead' in JOBS:  # 헤어 확대: 머리만 여러 각도
    HAIR_ON = HAIROB is not None; HT = (0, 0, 0.99)
    for tag, az, el in (('hh_front', 0, 4), ('hh_q', 35, 8), ('hh_side', 90, 4), ('hh_bq', 145, 8), ('hh_back', 180, 4), ('hh_top', 20, 55), ('hh_low', 30, -18), ('hh_q2', -40, 12)):
        if os.environ.get('HV') and tag[3:] not in os.environ['HV'].split(','): continue
        shoot(tag, az, el, HT, 3.3)
    HAIR_ON = False
if 'pose' in JOBS:
    POSES.pop('wave_old', None); POSES.pop('cheer', None)
    for name, fn in POSES.items():
        reset(); fn(); shoot('p_' + name, 35, 14, (0, 0, 0.72), 5.0); shoot('p_' + name + '_b', 150, 14, (0, 0, 0.72), 5.0, face=False)
    reset()
if 'gglb' in JOBS:      # 게임 시험용: 얼굴을 꼭짓점 색으로 구워 몸과 한 덩어리(스킨 메시 1개, 재질 1개)로 내보냄. GTRI = 몸 삼각형 수 목표, GFACE = 얼굴 파츠 감축 비율
    reset(); tgt = int(os.environ.get('GTRI', 0)); fr = float(os.environ.get('GFACE', 1.0))
    def paint(ob, rgb):
        ca = ob.data.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); ca.data.foreach_set('color', np.tile(np.array([*rgb, 1.0], np.float32), len(ob.data.vertices)))
    def dec(ob, ratio):
        if ratio >= 1: return
        bpy.context.view_layer.objects.active = ob; dm = ob.modifiers.new('Dec', 'DECIMATE'); dm.ratio = ratio
        bpy.ops.object.modifier_move_to_index(modifier='Dec', index=0); bpy.ops.object.modifier_apply(modifier='Dec')
    for o in FACE:                                        # 눈썹·입은 곡선 → 메시로
        if o.type != 'MESH':
            bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.convert(target='MESH')
    if tgt: dec(body, tgt / len(body.data.polygons))
    paint(body, srgb('#e4b491'))
    COLS = {'Eye': srgb('#2b211e'), 'EyeHi': (1, 1, 1), 'Brow': srgb('#2b211e'), 'Cheek': srgb('#f29a8e'), 'Mouth': srgb('#8a3b33')}
    for o in FACE:
        dec(o, fr); mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = Matrix.Identity(4); o.data.transform(mw)
        o.data.update(); tot = sum(pl.area for pl in o.data.polygons); Nn = sum((pl.normal * pl.area for pl in o.data.polygons), Vector())   # 면이 바깥(얼굴 앞, -Y)을 보게: 게임은 뒷면을 안 그림
        if Nn.length > 0.2 * tot: flip = Nn.y > 0
        else:
            bm = bmesh.new(); bm.from_mesh(o.data); flip = bm.calc_volume(signed=True) < 0; bm.free()
        if flip: o.data.flip_normals(); o.data.update()
        print('FACE', o.name, 'flip' if flip else 'ok', round(Nn.length / max(tot, 1e-9), 2))
        key = max((k for k in COLS if o.name.startswith(k)), key=len); paint(o, COLS[key])
        g = o.vertex_groups.new(name='head'); g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    bpy.ops.object.select_all(action='DESELECT')
    for o in FACE + [body]: o.select_set(True)
    bpy.context.view_layer.objects.active = body; bpy.ops.object.join()
    vc = bpy.data.materials.new('clay_vc'); vc.use_nodes = True; bb = node(vc.node_tree, 'BSDF_PRINCIPLED'); bb.inputs['Roughness'].default_value = 0.8
    an = vc.node_tree.nodes.new('ShaderNodeVertexColor'); an.layer_name = 'Col'; vc.node_tree.links.new(an.outputs['Color'], bb.inputs['Base Color'])
    body.data.materials.clear(); body.data.materials.append(vc)
    for pl in body.data.polygons: pl.material_index = 0; pl.use_smooth = True
    body.data.color_attributes.active_color = body.data.color_attributes['Col']; body.data.color_attributes.render_color_index = 0
    bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); rig.select_set(True)
    out = os.path.join(OUT, os.environ.get('GNAME', 'b15_game') + '.glb')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_skins=True, export_yup=True, export_animations=False)
    print('GGLB', out, len(body.data.polygons), 'tris', os.path.getsize(out))
if 'glb' in JOBS:
    for o in FACE: o.select_set(False)
    dm = body.modifiers.new('Dec', 'DECIMATE'); dm.ratio = float(os.environ.get('DEC', 0.06))
    bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_move_to_index(modifier='Dec', index=0)
    gp.hide_set(True); bpy.data.objects.remove(gp)
    out = os.path.join(OUT, 'base15.glb')
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_apply=True, export_skins=True, export_yup=True, export_animations=False)
    print('GLB', os.path.getsize(out))
