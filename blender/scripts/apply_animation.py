# blender/scripts/apply_animation.py
import bpy
import sys
import json
from pathlib import Path
import math

FRAME_RATE = 24


def apply_ease(obj, data_path, index=None):
    action = obj.animation_data.action
    for fcurve in action.fcurves:
        if fcurve.data_path == data_path:
            if index is None or fcurve.array_index == index:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'BEZIER'

COMMON_WAVE_BONES = [
    "RightArm","right_arm","RightArm_fk","upper_arm.R","UpperArm_R","MixamoRightArm",
    "mixamorig:RightArm","mixamorig_RightArm","RightShoulder","shoulder.R","shoulder_right"
]

def apply_jump(obj, start_frame, duration_frames, params):
    height = params.get("height", 2.0)

    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    obj.location.z = 0
    obj.keyframe_insert(data_path="location", frame=start_frame)

    obj.location.z = height
    obj.keyframe_insert(data_path="location", frame=mid_frame)

    obj.location.z = 0
    obj.keyframe_insert(data_path="location", frame=end_frame)

    apply_ease(obj, "location", index=2)


def apply_wave(obj, start_frame, duration_frames, params):
    speed = params.get("speed", "normal")
    intensity = params.get("intensity", 1.0)

    speed_multiplier = {
        "slow": 1.5,
        "normal": 1.0,
        "fast": 0.7
    }.get(speed, 1.0)

    adjusted_duration = int(duration_frames * speed_multiplier)

    mid_frame = start_frame + adjusted_duration // 2
    end_frame = start_frame + adjusted_duration

    obj.rotation_euler.z = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)

    obj.rotation_euler.z = intensity
    obj.keyframe_insert(data_path="rotation_euler", frame=mid_frame)

    obj.rotation_euler.z = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)

    apply_ease(obj, "rotation_euler", index=2)

    return adjusted_duration


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    if len(argv) < 2:
        raise RuntimeError("Expected arguments: <timeline.json> <output.blend>")

    timeline_path = Path(argv[0])
    output_blend_path = Path(argv[1])

    bpy.ops.wm.read_factory_settings(use_empty=True)

    with open(timeline_path, "r") as f:
        timeline_data = json.load(f)
def get_args():
    argv = sys.argv
    if "--" in argv:
        idx = argv.index("--")
        args = argv[idx+1:]
    else:
        args = []
    if len(args) < 3:
        raise SystemExit("Usage: blender --background --python apply_animation.py -- timeline.json model_path output.blend")
    return Path(args[0]), Path(args[1]), Path(args[2])

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_model(model_path: Path):
    model_path = Path(model_path)
    ext = model_path.suffix.lower()
    # handle common typo .gbl -> .glb
    if ext == ".gbl":
        ext = ".glb"

    imported_objects = []

    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = "AnimatedObject"
    if ext in [".fbx"]:
        bpy.ops.import_scene.fbx(filepath=str(model_path))
        imported_objects = list(bpy.context.selected_objects)
    elif ext in [".glb", ".gltf"]:
        bpy.ops.import_scene.gltf(filepath=str(model_path))
        imported_objects = list(bpy.context.selected_objects)
    elif ext in [".obj"]:
        bpy.ops.import_scene.obj(filepath=str(model_path))
        imported_objects = list(bpy.context.selected_objects)
    else:
        # try gltf import as a last resort
        try:
            bpy.ops.import_scene.gltf(filepath=str(model_path))
            imported_objects = list(bpy.context.selected_objects)
        except Exception as e:
            raise RuntimeError(f"Unsupported model format: {ext}") from e

    if not imported_objects:
        raise RuntimeError("Import succeeded but no objects were selected/imported.")

    # Prefer armature if present
    armature_objs = [o for o in imported_objects if o.type == "ARMATURE"]
    if armature_objs:
        arm = armature_objs[0]
        return arm  # return armature object as main anim target

    # Otherwise return the first mesh object
    mesh_objs = [o for o in imported_objects if o.type == "MESH"]
    if mesh_objs:
        return mesh_objs[0]

    # fallback to active object
    return bpy.context.view_layer.objects.active

def find_wave_bone_name(armature_obj):
    if armature_obj is None:
        return None
    for name in COMMON_WAVE_BONES:
        if name in armature_obj.data.bones.keys():
            return name
    # fuzzy search: try find bone with 'arm' in name
    for b in armature_obj.data.bones:
        if "arm" in b.name.lower():
            return b.name
    return None

def keyframe_pose_bone_rotation(arm_obj, bone_name, frame, rotation_euler):
    # rotation_euler is tuple (x,y,z) in radians
    pb = arm_obj.pose.bones.get(bone_name)
    if pb is None:
        return
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = rotation_euler
    # Insert keyframe on armature object data path for pose bone
    arm_obj.keyframe_insert(data_path=f'pose.bones["{bone_name}"].rotation_euler', frame=frame)

def apply_jump(target_obj, start_frame, duration_frames, height=1.5):
    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    # If this is an armature, apply root motion on object location
    target_obj.location = (0, 0, 0)
    target_obj.keyframe_insert(data_path="location", frame=start_frame)

    target_obj.location = (0, 0, height)
    target_obj.keyframe_insert(data_path="location", frame=mid_frame)

    target_obj.location = (0, 0, 0)
    target_obj.keyframe_insert(data_path="location", frame=end_frame)

def apply_wave(target_obj, start_frame, duration_frames, armature_bone=None):
    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    if armature_bone and target_obj.type == "ARMATURE":
        # animate pose bone rotation (simple wave around X)
        # neutral
        keyframe_pose_bone_rotation(target_obj, armature_bone, start_frame, (0.0, 0.0, 0.0))
        # raised
        keyframe_pose_bone_rotation(target_obj, armature_bone, mid_frame, (math.radians(60), 0.0, 0.0))
        # neutral
        keyframe_pose_bone_rotation(target_obj, armature_bone, end_frame, (0.0, 0.0, 0.0))
    else:
        # fallback: rotate the object around Z
        target_obj.rotation_euler = (0, 0, 0)
        target_obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)
        target_obj.rotation_euler = (0, 0, 1.0)
        target_obj.keyframe_insert(data_path="rotation_euler", frame=mid_frame)
        target_obj.rotation_euler = (0, 0, 0)
        target_obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)

def apply_timeline(timeline_path: Path, model_path: Path, out_blend: Path):
    with open(timeline_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # import model and choose target (armature preferred)
    imported_target = import_model(model_path)

    fps = bpy.context.scene.render.fps
    if not fps:
        fps = FRAME_RATE
        bpy.context.scene.render.fps = fps

    # if armature, try to find a bone to wave
    arm_bone_name = None
    if imported_target and imported_target.type == "ARMATURE":
        arm_bone_name = find_wave_bone_name(imported_target)

    current_frame = 1
    for entry in data.get("timeline", []):
        typ = entry.get("type")
        start_frame = current_frame
        duration_frames = max(1, int((entry.get("end_time", entry.get("start_time", start_frame)) - entry.get("start_time", 0)) * fps))
        if typ == "jump":
            apply_jump(imported_target, start_frame, duration_frames, height=entry.get("params", {}).get("height", 1.5))
        elif typ == "wave":
            apply_wave(imported_target, start_frame, duration_frames, armature_bone=arm_bone_name)
        else:
            # fallback: insert no-op keyframes to mark timeline
            imported_target.keyframe_insert(data_path="location", frame=start_frame)
            imported_target.keyframe_insert(data_path="location", frame=start_frame + duration_frames)

    for action in timeline_data["timeline"]:
        duration_frames = int(
            (action["end_time"] - action["start_time"]) * FRAME_RATE
        )

        params = action.get("params", {})

        if action["type"] == "jump":
            apply_jump(obj, current_frame, duration_frames, params)
            current_frame += duration_frames
        current_frame += duration_frames

        elif action["type"] == "wave":
            actual_duration = apply_wave(obj, current_frame, duration_frames, params)
            current_frame += actual_duration

    bpy.context.scene.frame_end = current_frame + 10

    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path))
    print(f"Saved animated blend file to {output_blend_path}")
    print("[DEBUG] Action params received:", params)

    # save the resulting blend
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
    print(f"Saved animated blend file to {out_blend}")

def main():
    timeline_path, model_path, out_blend = get_args()
    clear_scene()
    apply_timeline(timeline_path, model_path, out_blend)

if __name__ == "__main__":
    main()

