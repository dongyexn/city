# Blender Python script: chibi clay head + face base
# Target: soft, rounded Nendoroid / Animal-Crossing-like proportions.
# Coordinate convention: character faces toward -Y; Z is up.
# Run in Blender's Scripting workspace. No external add-ons required.

import bpy
import math
from mathutils import Vector

# ------------------------------------------------------------
# PARAMETER BLOCK — adjust these values to match your character
# ------------------------------------------------------------
HEAD_CENTER = (0.0, 0.0, 2.00)
HEAD_RADIUS = (0.82, 0.66, 0.98)   # width, depth, height
HEAD_SEGMENTS = 96
HEAD_RINGS = 64

SKIN_COLOR = (0.91, 0.82, 0.77, 1.0)
EYE_OUTLINE_COLOR = (0.105, 0.075, 0.19, 1.0)
EYE_WHITE_COLOR = (0.93, 0.88, 0.98, 1.0)
IRIS_COLOR = (0.39, 0.22, 0.72, 1.0)
IRIS_LIGHT_COLOR = (0.63, 0.43, 0.91, 1.0)
PUPIL_COLOR = (0.12, 0.075, 0.24, 1.0)
BLUSH_COLOR = (0.91, 0.43, 0.48, 1.0)
MOUTH_COLOR = (0.53, 0.19, 0.22, 1.0)

EYE_X = 0.335
EYE_Z = 2.045
EYE_WIDTH = 0.205
EYE_HEIGHT = 0.275
EYE_DEPTH = 0.085
EYE_SPACING = 0.67

CHEEK_X = 0.565
CHEEK_Z = 1.79
CHEEK_SIZE = (0.105, 0.035, 0.055)

# ------------------------------------------------------------
# SCENE / COLLECTION HELPERS
# ------------------------------------------------------------
def get_or_create_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

COL = get_or_create_collection("CHARACTER_HEAD_FACE")

def move_to_collection(obj, collection=COL):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)

def make_clay_material(name, color, roughness=0.78, subsurface=0.035):
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
    elif "Subsurface" in bsdf.inputs:
        bsdf.inputs["Subsurface"].default_value = subsurface
    return mat

MAT_SKIN = make_clay_material("Clay_Skin", SKIN_COLOR, 0.82, 0.055)
MAT_EYE_OUT = make_clay_material("Eye_Deep_Purple", EYE_OUTLINE_COLOR, 0.48, 0.0)
MAT_EYE_WHITE = make_clay_material("Eye_Lavender_White", EYE_WHITE_COLOR, 0.42, 0.0)
MAT_IRIS = make_clay_material("Iris_Purple", IRIS_COLOR, 0.38, 0.0)
MAT_IRIS_LIGHT = make_clay_material("Iris_Light_Purple", IRIS_LIGHT_COLOR, 0.38, 0.0)
MAT_PUPIL = make_clay_material("Pupil", PUPIL_COLOR, 0.35, 0.0)
MAT_BLUSH = make_clay_material("Soft_Rose_Blush", BLUSH_COLOR, 0.88, 0.02)
MAT_MOUTH = make_clay_material("Mouth_Rose", MOUTH_COLOR, 0.75, 0.0)

def add_uv_sphere(name, location, scale, material, segments=48, rings=32):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=rings, radius=1.0, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for p in obj.data.polygons:
        p.use_smooth = True
    if material:
        obj.data.materials.append(material)
    move_to_collection(obj)
    return obj

def front_surface_y(x, z):
    # Approximate front surface of the ellipsoidal head.
    rx, ry, rz = HEAD_RADIUS
    cx, cy, cz = HEAD_CENTER
    nx = (x - cx) / rx
    nz = (z - cz) / rz
    inside = max(0.05, 1.0 - nx * nx - nz * nz)
    return cy - ry * math.sqrt(inside)

def add_curve_line(name, points, bevel_depth, material, resolution=16):
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 5
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for bp, co in zip(spline.bezier_points, points):
        bp.co = co
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    COL.objects.link(obj)
    obj.data.materials.append(material)
    return obj

# ------------------------------------------------------------
# REMOVE PREVIOUS GENERATED HEAD OBJECTS (safe to rerun)
# ------------------------------------------------------------
for obj in list(COL.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# ------------------------------------------------------------
# HEAD: custom-shaped smooth ellipsoid with a gently tapered chin
# ------------------------------------------------------------
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=HEAD_SEGMENTS,
    ring_count=HEAD_RINGS,
    radius=1.0,
    location=HEAD_CENTER
)
head = bpy.context.object
head.name = "HEAD_Smooth_Rounded_Base"
head.scale = HEAD_RADIUS
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Slightly narrow the lower jaw while keeping a soft rounded chin.
for v in head.data.vertices:
    z_norm = v.co.z / HEAD_RADIUS[2]
    if z_norm < -0.18:
        t = min(1.0, max(0.0, (-z_norm - 0.18) / 0.82))
        jaw_factor = 1.0 - 0.16 * (t ** 1.35)
        v.co.x *= jaw_factor
    # Flatten the very front slightly, avoiding a spherical "ball" face.
    if v.co.y < -HEAD_RADIUS[1] * 0.72:
        v.co.y = -HEAD_RADIUS[1] * 0.72 + (v.co.y + HEAD_RADIUS[1] * 0.72) * 0.35

for p in head.data.polygons:
    p.use_smooth = True
head.data.materials.append(MAT_SKIN)
move_to_collection(head)

# Subtle ears, mostly hidden by hair in the final design.
for side in (-1, 1):
    add_uv_sphere(
        f"Ear_{'L' if side < 0 else 'R'}",
        (side * 0.795, -0.005, 1.93),
        (0.105, 0.105, 0.17),
        MAT_SKIN, 40, 28
    )

# ------------------------------------------------------------
# EYES: layered, soft anime eyes. Front of character is -Y.
# ------------------------------------------------------------
for side, label in [(-1, "L"), (1, "R")]:
    x = side * EYE_X
    z = EYE_Z
    y = front_surface_y(x, z)

    # Dark plum outer rim / socket
    add_uv_sphere(
        f"Eye_{label}_Outer_Rim",
        (x, y - 0.018, z),
        (EYE_WIDTH * 1.13, EYE_DEPTH, EYE_HEIGHT * 1.10),
        MAT_EYE_OUT
    )
    # Pale lavender eye base
    add_uv_sphere(
        f"Eye_{label}_Sclera",
        (x, y - 0.083, z + 0.005),
        (EYE_WIDTH * 0.91, EYE_DEPTH * 0.48, EYE_HEIGHT * 0.91),
        MAT_EYE_WHITE
    )
    # Large purple iris
    add_uv_sphere(
        f"Eye_{label}_Iris",
        (x, y - 0.119, z - 0.012),
        (EYE_WIDTH * 0.70, EYE_DEPTH * 0.32, EYE_HEIGHT * 0.73),
        MAT_IRIS
    )
    # Lighter lower iris area
    add_uv_sphere(
        f"Eye_{label}_Iris_Lower_Glow",
        (x, y - 0.145, z - 0.095),
        (EYE_WIDTH * 0.47, EYE_DEPTH * 0.16, EYE_HEIGHT * 0.29),
        MAT_IRIS_LIGHT
    )
    # Pupil
    add_uv_sphere(
        f"Eye_{label}_Pupil",
        (x, y - 0.155, z + 0.045),
        (EYE_WIDTH * 0.30, EYE_DEPTH * 0.17, EYE_HEIGHT * 0.40),
        MAT_PUPIL
    )
    # Two small matte highlights
    add_uv_sphere(
        f"Eye_{label}_Highlight_Main",
        (x - side * 0.045, y - 0.177, z + 0.115),
        (0.047, 0.018, 0.060),
        MAT_EYE_WHITE, 32, 20
    )
    add_uv_sphere(
        f"Eye_{label}_Highlight_Small",
        (x + side * 0.043, y - 0.176, z - 0.075),
        (0.020, 0.012, 0.025),
        MAT_EYE_WHITE, 24, 16
    )

    # Soft upper lash accent, kept short and rounded.
    add_curve_line(
        f"Eye_{label}_Upper_Lash",
        [
            (x - side * 0.17, y - 0.045, z + 0.205),
            (x, y - 0.095, z + 0.292),
            (x + side * 0.15, y - 0.045, z + 0.205),
        ],
        0.018, MAT_EYE_OUT
    )

# ------------------------------------------------------------
# BLUSH: small soft pink ovals on the cheeks
# ------------------------------------------------------------
for side, label in [(-1, "L"), (1, "R")]:
    x = side * CHEEK_X
    z = CHEEK_Z
    y = front_surface_y(x, z)
    blush = add_uv_sphere(
        f"Cheek_Blush_{label}",
        (x, y - 0.022, z),
        CHEEK_SIZE,
        MAT_BLUSH, 40, 24
    )
    blush.rotation_euler[1] = side * math.radians(-12)

# ------------------------------------------------------------
# MOUTH: tiny, simple, softly curved "w" smile
# ------------------------------------------------------------
mouth_z = 1.735
mouth_y = front_surface_y(0.0, mouth_z) - 0.035
add_curve_line(
    "Mouth_Tiny_W_Smile",
    [
        (-0.052, mouth_y, mouth_z + 0.006),
        (-0.026, mouth_y - 0.008, mouth_z - 0.012),
        (0.0, mouth_y - 0.012, mouth_z + 0.002),
        (0.026, mouth_y - 0.008, mouth_z - 0.012),
        (0.052, mouth_y, mouth_z + 0.006),
    ],
    0.012, MAT_MOUTH, 20
)

# Tiny understated nose is intentionally omitted to preserve the reference look.

# ------------------------------------------------------------
# OPTIONAL: select head objects for easy inspection
# ------------------------------------------------------------
bpy.ops.object.select_all(action="DESELECT")
head.select_set(True)
bpy.context.view_layer.objects.active = head

print("Created smooth chibi head + face in collection: CHARACTER_HEAD_FACE")
print("Front direction: -Y | Head center:", HEAD_CENTER, "| Head radii:", HEAD_RADIUS)
