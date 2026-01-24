# blender/run_blender.py
import json
import subprocess
from pathlib import Path
from config import BLENDER_PATH, BLENDER_SCRIPT

def run_blender(animation_timeline, model_path: Path, output_blend: Path, capture_output: bool = False):
    """
    animation_timeline: pydantic model (TimedAnimationPlan)
    model_path: Path to input model (fbx/glb/gltf/obj)
    output_blend: Path to write final .blend
    """
    output_blend = Path(output_blend)
    temp_json = output_blend.with_suffix(".json")

    # pydantic v2 or v1 compatibility
    try:
        data = animation_timeline.model_dump()
    except Exception:
        try:
            data = animation_timeline.dict()
        except Exception:
            data = animation_timeline

    with open(temp_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Resolve blender script path to absolute
    blender_script_path = Path(BLENDER_SCRIPT)
    if not blender_script_path.is_absolute():
        blender_script_path = (Path.cwd() / blender_script_path).resolve()

    cmd = [
        BLENDER_PATH,
        "-b",
        "--python", str(blender_script_path),
        "--",
        str(temp_json),
        str(Path(model_path).resolve()),
        str(output_blend.resolve()),
    ]

    print("Launching Blender:", " ".join(f'"{p}"' for p in cmd))

    if capture_output:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr
    else:
        subprocess.run(cmd, check=True)
        return 0, None, None
