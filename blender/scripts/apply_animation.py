import bpy
import sys
import json
from pathlib import Path

FRAME_RATE = 24


def apply_ease(obj, data_path, index=None):
    action = obj.animation_data.action
    for fcurve in action.fcurves:
        if fcurve.data_path == data_path:
            if index is None or fcurve.array_index == index:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = 'BEZIER'


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

    print("Timeline received:", timeline_data)

    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = "AnimatedObject"

    current_frame = 1

    for action in timeline_data["timeline"]:
        duration_frames = int(
            (action["end_time"] - action["start_time"]) * FRAME_RATE
        )

        params = action.get("params", {})

        if action["type"] == "jump":
            apply_jump(obj, current_frame, duration_frames, params)
            current_frame += duration_frames

        elif action["type"] == "wave":
            actual_duration = apply_wave(obj, current_frame, duration_frames, params)
            current_frame += actual_duration

    bpy.context.scene.frame_end = current_frame + 10

    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path))
    print(f"Saved animated blend file to {output_blend_path}")


if __name__ == "__main__":
    main()

