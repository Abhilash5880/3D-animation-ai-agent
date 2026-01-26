import bpy
import sys
import json
from pathlib import Path

FRAME_RATE = 24


# ---------------- Utilities ---------------- #

def force_bezier(action, data_path, index=None):
    for fcurve in action.fcurves:
        if fcurve.data_path == data_path:
            if index is None or fcurve.array_index == index:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = "BEZIER"


def get_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def get_root_object():
    for obj in bpy.context.scene.objects:
        if obj.type in {"ARMATURE", "MESH"}:
            return obj
    raise RuntimeError("No animation target found.")


def get_wave_bone(armature):
    candidates = [
        "mixamorig:RightHand",
        "mixamorig:RightForeArm",
        "RightHand",
        "hand.R",
        "forearm.R",
    ]
    for name in candidates:
        if name in armature.pose.bones:
            return armature.pose.bones[name]
    raise RuntimeError("Wave bone not found.")


# ---------------- Actions ---------------- #

def apply_jump(obj, start_frame, duration_frames, height):
    mid = start_frame + duration_frames // 2
    end = start_frame + duration_frames
    base = obj.location.z

    obj.location.z = base
    obj.keyframe_insert("location", frame=start_frame)

    obj.location.z = base + height
    obj.keyframe_insert("location", frame=mid)

    obj.location.z = base
    obj.keyframe_insert("location", frame=end)

    force_bezier(obj.animation_data.action, "location", 2)


def apply_wave(armature, start_frame, duration_frames):
    bone = get_wave_bone(armature)
    mid = start_frame + duration_frames // 2
    end = start_frame + duration_frames

    bone.rotation_mode = "XYZ"

    bone.rotation_euler.z = 0
    bone.keyframe_insert("rotation_euler", frame=start_frame)

    bone.rotation_euler.z = 0.9
    bone.keyframe_insert("rotation_euler", frame=mid)

    bone.rotation_euler.z = 0
    bone.keyframe_insert("rotation_euler", frame=end)

    force_bezier(
        armature.animation_data.action,
        f'pose.bones["{bone.name}"].rotation_euler',
        2,
    )


# ---------------- Main ---------------- #

def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    timeline_path, model_path, output_path = map(Path, argv)

    bpy.ops.wm.read_factory_settings(use_empty=True)

    if model_path.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(model_path))
    else:
        bpy.ops.import_scene.gltf(filepath=str(model_path))

    root = get_root_object()
    armature = get_armature()

    target = armature if armature else root
    target.animation_data_create()
    target.animation_data.action = bpy.data.actions.new("AI_Action")

    with open(timeline_path) as f:
        timeline = json.load(f)["timeline"]

    frame = 1

    for action in timeline:
        duration_frames = int(
            (action["end_time"] - action["start_time"]) * FRAME_RATE
        )

        if action["type"] == "jump":
            height = action.get("params", {}).get("height", 2.0)
            apply_jump(root, frame, duration_frames, height)

        elif action["type"] == "wave":
            if armature:
                apply_wave(armature, frame, duration_frames)

        frame += duration_frames

    bpy.context.scene.frame_end = frame + 5
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
    print(f"Blend file generated at {output_path}")


if __name__ == "__main__":
    main()
