"""개·고양이: 걷기/대기/앉기 동작을 절차적으로 넣고 웹용 GLB로 내보내기(텍스처 1024로 축소)"""
import bpy, sys, math
from mathutils import Vector, Quaternion, Matrix
f, out, texout = sys.argv[-3], sys.argv[-2], sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=f, load_ui=False)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
A = arm.matrix_world.to_3x3().normalized()
B = arm.data.bones
def has(n): return n in B
def wq(name, axis_world, deg):
    """월드 축 기준 회전을 뼈 로컬 회전(쿼터니언)으로"""
    ax = (B[name].matrix_local.to_3x3().inverted() @ (A.inverted() @ Vector(axis_world))).normalized()
    return Quaternion(ax, math.radians(deg))
def wl(name, vec_world):
    return B[name].matrix_local.to_3x3().inverted() @ (arm.matrix_world.to_3x3().inverted() @ Vector(vec_world))
X, Z = (1, 0, 0), (0, 0, 1)
for pb in arm.pose.bones: pb.rotation_mode = 'QUATERNION'
H = max((mesh.matrix_world @ Vector(c)).z for c in mesh.bound_box)

def key_all(fr, rots, locs):
    for pb in arm.pose.bones:
        q = Quaternion()
        for n, qq in rots.get(pb.name, []): q = qq @ q
        pb.rotation_quaternion = q; pb.keyframe_insert('rotation_quaternion', frame=fr)
        pb.location = locs.get(pb.name, Vector()); pb.keyframe_insert('location', frame=fr)

def make(name, n, fn):
    act = bpy.data.actions.new(name); arm.animation_data_create(); arm.animation_data.action = act
    for fr in range(0, n + 1, 2):
        rots, locs = fn(fr / n * 2 * math.pi)
        key_all(fr, rots, locs)
    arm.animation_data.action = None
    tr = arm.animation_data.nla_tracks.new(); tr.name = name; tr.strips.new(name, 0, act); tr.mute = True
    act.use_fake_user = True
    return act

def R(d, name, axis, deg):
    if has(name): d.setdefault(name, []).append((name, wq(name, axis, deg)))

def tail(d, t, amp, speed=1):
    for i, nm in enumerate(['Tail', 'Tail1', 'Tail2', 'Tail3']): R(d, nm, Z, amp * math.sin(t * speed - i * 0.6))

def walk(t):
    d, L = {}, {}
    for leg, ph in [('LeftArm', 0), ('RightUpLeg', 0), ('RightArm', math.pi), ('LeftUpLeg', math.pi)]:
        s = math.sin(t + ph); R(d, leg, X, 24 * s)                                    # 앞뒤로 흔들기(대각선 짝)
        low = {'LeftArm': 'LeftForeArm', 'RightArm': 'RightForeArm', 'LeftUpLeg': 'LeftLeg', 'RightUpLeg': 'RightLeg'}[leg]
        R(d, low, X, (-1 if 'Arm' in leg else 1) * 28 * max(0, math.cos(t + ph)))   # 들어 올릴 때 무릎 굽힘
    R(d, 'Spine', Z, 3 * math.sin(t)); R(d, 'Head', X, 3 * math.sin(2 * t)); R(d, 'Neck', Z, -2 * math.sin(t))
    tail(d, t, 18, 2)
    for e in ['LeftEar', 'RightEar']: R(d, e, X, 6 * math.sin(2 * t + 1))
    L['Root'] = wl('Root', (0, 0, 0.012 * H * abs(math.cos(t))))
    return d, L

def idle(t):
    d, L = {}, {}
    R(d, 'Spine1', X, 1.5 * math.sin(t)); R(d, 'Head', Z, 6 * math.sin(t)); R(d, 'Head', X, 2 * math.sin(2 * t))
    tail(d, t, 25, 3)
    for e in ['LeftEar', 'RightEar']: R(d, e, X, 4 * math.sin(t + 0.5))
    return d, L

def sit(t):
    import os
    d, L = {}, {}
    rp, ul, lg, ft, ar, nk, hd, dz = [float(x) for x in os.environ.get('SITP', '-22,62,-75,35,20,14,10,0.14').split(',')]
    R(d, 'Root', X, rp)                                                      # 몸 앞쪽을 들어 엉덩이를 내림
    for s in ['Left', 'Right']:
        R(d, s + 'UpLeg', X, ul); R(d, s + 'Leg', X, lg); R(d, s + 'Foot', X, ft)   # 뒷다리 접기
        R(d, s + 'Arm', X, ar)                                                # 앞다리를 세워 바닥 짚기
    R(d, 'Neck', X, nk); R(d, 'Head', X, hd + 2 * math.sin(t)); tail(d, t, 12, 2)   # 고개는 다시 앞을 보게
    L['Root'] = wl('Root', (0, 0.03 * H, -dz * H))
    return d, L

make('Idle', 48, idle); make('Walk', 24, walk); make('Sit', 48, sit)
print('ACTIONS', [a.name for a in bpy.data.actions])

# 텍스처 1024로 줄이기(웹용)
import os
for img in list(bpy.data.images):
    if img.filepath:
        new = bpy.data.images.load(os.path.join(texout, os.path.splitext(os.path.basename(img.filepath))[0] + (os.environ.get("TEXEXT") or os.path.splitext(img.filepath)[1])))
        for m in bpy.data.materials:
            if m.node_tree:
                for nd in m.node_tree.nodes:
                    if nd.type == 'TEX_IMAGE' and nd.image == img: nd.image = new
if '--preview' not in sys.argv:
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', export_animations=True, export_animation_mode='ACTIONS', export_skins=True, export_apply=False)
    print('EXPORTED', out)
