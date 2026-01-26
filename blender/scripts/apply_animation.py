import bpy
import sys
import json
from pathlib import Path

FRAME_RATE = 24


# -------------------------------------------------
# Utility helpers
# -------------------------------------------------

def force_bezier(action, data_path, index=None):
    for fcurve in action.fcurves:
        if fcurve.data_path == data_path:
            if index is None or fcurve.array_index == index:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'BEZIER'


def get_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == "ARMATURE":
            return obj
    return None


def get_root_object():
    for obj in bpy.context.scene.objects:
        if obj.type in {"ARMATURE", "MESH"}:
            return obj
    raise RuntimeError("No valid animation target found.")


def get_wave_bone(armature):
    """
    Try common Mixamo / generic bone names.
    """
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

    raise RuntimeError("No suitable wave bone found.")


# -------------------------------------------------
# Animation actions
# -------------------------------------------------

def apply_jump(obj, start_frame, duration_frames, height=2.0):
    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    base_z = obj.location.z

    obj.location.z = base_z - height * 0.15
    obj.keyframe_insert("location", frame=start_frame)

    obj.location.z = base_z + height
    obj.keyframe_insert("location", frame=mid_frame)

    obj.location.z = base_z
    obj.keyframe_insert("location", frame=end_frame)

    force_bezier(obj.animation_data.action, "location", index=2)


def apply_wave(armature, start_frame, duration_frames):
    bone = get_wave_bone(armature)

    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    bone.rotation_mode = "XYZ"

    bone.rotation_euler.z = 0.0
    bone.keyframe_insert("rotation_euler", frame=start_frame)

    bone.rotation_euler.z = 0.9
    bone.keyframe_insert("rotation_euler", frame=mid_frame)

    bone.rotation_euler.z = 0.0
    bone.keyframe_insert("rotation_euler", frame=end_frame)

    action = armature.animation_data.action
    force_bezier(action, f'pose.bones["{bone.name}"].rotation_euler', index=2)


# -------------------------------------------------
# Main execution
# -------------------------------------------------

def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]

    if len(argv) < 3:
        raise RuntimeError(
            "Usage: apply_animation.py <timeline.json> <model.glb> <output.blend>"
        )

    timeline_path = Path(argv[0])
    model_path = Path(argv[1])
    output_path = Path(argv[2])

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(model_path))

    root_obj = get_root_object()
    armature = get_armature()

    target = armature if armature else root_obj
    target.animation_data_create()
    target.animation_data.action = bpy.data.actions.new("AI_Animation")

    with open(timeline_path, "r") as f:
        timeline = json.load(f)

    current_frame = 1

    for action in timeline["timeline"]:
        duration_frames = int(
            (action["end_time"] - action["start_time"]) * FRAME_RATE
        )

        if action["type"] == "jump":
            height = action.get("params", {}).get("height", 2.0)
            apply_jump(root_obj, current_frame, duration_frames, height)

        elif action["type"] == "wave":
            if armature:
                apply_wave(armature, current_frame, duration_frames)
            else:
                # fallback for non-rigged models
                root_obj.rotation_euler.z = 0
                root_obj.keyframe_insert("rotation_euler", frame=current_frame)
                root_obj.rotation_euler.z = 0.8
                root_obj.keyframe_insert(
                    "rotation_euler", frame=current_frame + duration_frames // 2
                )
                root_obj.rotation_euler.z = 0
                root_obj.keyframe_insert(
                    "rotation_euler", frame=current_frame + duration_frames
                )

        current_frame += duration_frames

    bpy.context.scene.frame_end = current_frame + 5
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path))

    print(f"Blend file generated at: {output_path}")


if __name__ == "__main__":
    main()
