# Blender Python API — revised chibi clay head + face
# Character faces toward -Y. Z is up.
# This revision shortens the head, rounds the jaw, and embeds facial features
# closer to the head surface to avoid the "eyes glued onto an egg" appearance.

import bpy
import math

# ------------------------- PARAMETERS -------------------------
HEAD_CENTER = (0.0, 0.0, 2.0)
# Wider and shorter than v1: less egg-shaped, more chibi.
HEAD_RADIUS = (0.86, 0.64, 0.82)
HEAD_SEGMENTS = 128
HEAD_RINGS = 96

SKIN = (0.91, 0.83, 0.79, 1.0)
DARK = (0.12, 0.085, 0.20, 1.0)
EYE_BASE = (0.83, 0.73, 0.91, 1.0)
IRIS = (0.40, 0.25, 0.72, 1.0)
IRIS_LIGHT = (0.65, 0.48, 0.88, 1.0)
PUPIL = (0.16, 0.10, 0.27, 1.0)
WHITE = (0.98, 0.94, 1.0, 1.0)
BLUSH = (0.88, 0.48, 0.52, 1.0)
MOUTH = (0.55, 0.25, 0.29, 1.0)

EYE_X = 0.315
EYE_Z = 2.045
EYE_W = 0.165
EYE_H = 0.218
# Very shallow depth: facial layers sit close to the skin.
EYE_D = 0.026
CHEEK_X = 0.565
CHEEK_Z = 1.79

# ------------------------- COLLECTION -------------------------
COL_NAME = "CHIBI_HEAD_FACE_V2"
col = bpy.data.collections.get(COL_NAME)
if col is None:
    col = bpy.data.collections.new(COL_NAME)
    bpy.context.scene.collection.children.link(col)

# Remove only objects from this script's collection, so rerunning is safe.
for ob in list(col.objects):
    bpy.data.objects.remove(ob, do_unlink=True)

def move_to_col(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj

def material(name, color, roughness=0.8, subsurface=0.04):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    return mat

M_SKIN = material("V2_Clay_Skin", SKIN, 0.86, 0.07)
M_DARK = material("V2_Eye_Deep_Plum", DARK, 0.58, 0.0)
M_EYE = material("V2_Eye_Lavender", EYE_BASE, 0.52, 0.0)
M_IRIS = material("V2_Iris_Purple", IRIS, 0.48, 0.0)
M_IRIS_LIGHT = material("V2_Iris_Light", IRIS_LIGHT, 0.5, 0.0)
M_PUPIL = material("V2_Pupil", PUPIL, 0.48, 0.0)
M_WHITE = material("V2_Highlight", WHITE, 0.5, 0.0)
M_BLUSH = material("V2_Blush", BLUSH, 0.9, 0.02)
M_MOUTH = material("V2_Mouth", MOUTH, 0.82, 0.0)

def uv_sphere(name, loc, scale, mat, seg=64, rings=40):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=seg, ring_count=rings, radius=1.0, location=loc
    )
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in ob.data.polygons:
        p.use_smooth = True
    ob.data.materials.append(mat)
    move_to_col(ob)
    return ob

def face_y(x, z):
    # Ellipsoid front surface, with a slight allowance for the softened jaw.
    rx, ry, rz = HEAD_RADIUS
    cx, cy, cz = HEAD_CENTER
    q = 1.0 - ((x-cx)/rx)**2 - ((z-cz)/rz)**2
    return cy - ry * math.sqrt(max(0.08, q))

def curve(name, points, bevel, mat):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 24
    data.bevel_depth = bevel
    data.bevel_resolution = 6
    sp = data.splines.new("BEZIER")
    sp.bezier_points.add(len(points)-1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = p
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(name, data)
    col.objects.link(ob)
    ob.data.materials.append(mat)
    return ob

# ------------------------- HEAD SHAPE -------------------------
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=HEAD_SEGMENTS, ring_count=HEAD_RINGS,
    radius=1.0, location=HEAD_CENTER
)
head = bpy.context.object
head.name = "V2_HEAD_Rounded_Chibi"
head.scale = HEAD_RADIUS
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Subtle cheek fullness and a soft, rounded lower jaw.
for v in head.data.vertices:
    zn = v.co.z / HEAD_RADIUS[2]
    xn = v.co.x / HEAD_RADIUS[0]
    if zn < -0.12:
        t = min(1.0, max(0.0, (-zn - 0.12) / 0.88))
        v.co.x *= (1.0 - 0.10 * (t ** 1.4))
    # Gently fuller cheek zone; no sharp jaw corner.
    if -0.45 < zn < 0.12 and abs(xn) > 0.45:
        v.co.x *= 1.015

for p in head.data.polygons:
    p.use_smooth = True
head.data.materials.append(M_SKIN)
move_to_col(head)

# Small ears, set partly into the head (hair will cover most of them).
for s, side in [(-1, "L"), (1, "R")]:
    uv_sphere(
        f"V2_Ear_{side}",
        (s*0.815, -0.005, 1.91),
        (0.075, 0.070, 0.115), M_SKIN, 48, 32
    )

# ------------------------- EYES -------------------------
# Each eye is a shallow, layered oval, not a stack of deep protruding balls.
for s, side in [(-1, "L"), (1, "R")]:
    x, z = s*EYE_X, EYE_Z
    y = face_y(x, z)

    # Outer dark rim: mostly embedded in the face.
    uv_sphere(
        f"V2_Eye_{side}_Rim",
        (x, y-0.006, z),
        (EYE_W*1.08, EYE_D*0.72, EYE_H*1.08), M_DARK
    )
    # Soft lavender eye bed.
    uv_sphere(
        f"V2_Eye_{side}_Bed",
        (x, y-0.014, z),
        (EYE_W*0.91, EYE_D*0.52, EYE_H*0.91), M_EYE
    )
    # Iris.
    uv_sphere(
        f"V2_Eye_{side}_Iris",
        (x, y-0.022, z-0.006),
        (EYE_W*0.69, EYE_D*0.38, EYE_H*0.72), M_IRIS
    )
    # Lower iris gradient-like clay insert.
    uv_sphere(
        f"V2_Eye_{side}_Iris_Lower",
        (x, y-0.027, z-0.075),
        (EYE_W*0.46, EYE_D*0.23, EYE_H*0.27), M_IRIS_LIGHT
    )
    # Pupil.
    uv_sphere(
        f"V2_Eye_{side}_Pupil",
        (x, y-0.030, z+0.035),
        (EYE_W*0.27, EYE_D*0.22, EYE_H*0.37), M_PUPIL
    )
    # Small highlights, deliberately restrained.
    uv_sphere(
        f"V2_Eye_{side}_Highlight",
        (x-s*0.035, y-0.039, z+0.095),
        (0.027, 0.010, 0.035), M_WHITE, 32, 24
    )
    uv_sphere(
        f"V2_Eye_{side}_Highlight_Small",
        (x+s*0.030, y-0.038, z-0.065),
        (0.012, 0.007, 0.015), M_WHITE, 24, 16
    )

# ------------------------- CHEEKS -------------------------
for s, side in [(-1, "L"), (1, "R")]:
    x, z = s*CHEEK_X, CHEEK_Z
    y = face_y(x, z)
    cheek = uv_sphere(
        f"V2_Cheek_{side}",
        (x, y-0.006, z),
        (0.080, 0.018, 0.038), M_BLUSH, 48, 32
    )
    cheek.rotation_euler[1] = s * math.radians(-10)

# ------------------------- TINY MOUTH -------------------------
mz = 1.735
my = face_y(0.0, mz) - 0.012
curve(
    "V2_Mouth_Soft_W",
    [
        (-0.043, my, mz+0.003),
        (-0.022, my-0.002, mz-0.009),
        (0.0, my-0.003, mz-0.001),
        (0.022, my-0.002, mz-0.009),
        (0.043, my, mz+0.003),
    ],
    0.008, M_MOUTH
)

# Front view camera-like viewport orientation is not changed.
bpy.ops.object.select_all(action="DESELECT")
head.select_set(True)
bpy.context.view_layer.objects.active = head

print("V2 chibi head + face created.")
print("Front = -Y | Head radii =", HEAD_RADIUS)
