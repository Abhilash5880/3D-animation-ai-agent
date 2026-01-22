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


def apply_jump(obj, start_frame, duration_frames, height=2.0):
    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    # Start on ground
    obj.location.z = 0
    obj.keyframe_insert(data_path="location", frame=start_frame)

    # Jump peak
    obj.location.z = height
    obj.keyframe_insert(data_path="location", frame=mid_frame)

    # Land back
    obj.location.z = 0
    obj.keyframe_insert(data_path="location", frame=end_frame)

    apply_ease(obj, "location", index=2)  # Z-axis




def apply_wave(obj, start_frame, duration_frames):
    mid_frame = start_frame + duration_frames // 2
    end_frame = start_frame + duration_frames

    # Neutral rotation
    obj.rotation_euler.z = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)

    # Rotate right
    obj.rotation_euler.z = 1.0
    obj.keyframe_insert(data_path="rotation_euler", frame=mid_frame)

    # Back to neutral
    obj.rotation_euler.z = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    apply_ease(obj, "rotation_euler", index=2)  # Z rotation



def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :]

    if len(argv) < 2:
        raise RuntimeError("Expected arguments: <timeline.json> <output.blend>")

    timeline_path = Path(argv[0])
    output_blend_path = Path(argv[1])

    # Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Load timeline
    with open(timeline_path, "r") as f:
        timeline_data = json.load(f)

    print("Timeline received:", timeline_data)

    # Create object (placeholder character)
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = "AnimatedObject"

    current_frame = 1

    for action in timeline_data["timeline"]:
        repeat = action.get("repeat", 1)
        for _ in range(repeat):
            duration_frames = int(
                (action["end_time"] - action["start_time"]) * FRAME_RATE
            )

            if action["type"] == "jump":
                height = action.get("height", 2.0)
                apply_jump(obj, current_frame, duration_frames, height)


            elif action["type"] == "wave":
                apply_wave(obj, current_frame, duration_frames)

            current_frame += duration_frames

    bpy.context.scene.frame_end = current_frame + 10

    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend_path))
    print(f"Saved animated blend file to {output_blend_path}")


if __name__ == "__main__":
    main()
