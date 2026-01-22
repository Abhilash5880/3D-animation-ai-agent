import json
import subprocess
from pathlib import Path
from config import BLENDER_PATH, BLENDER_SCRIPT


def run_blender(animation_timeline: dict, output_blend: Path):
    temp_json = output_blend.with_suffix(".json")

    with open(temp_json, "w") as f:
        json.dump(animation_timeline.model_dump(), f, indent=2)


    cmd = [
        BLENDER_PATH,
        "-b",
        "--python", BLENDER_SCRIPT,
        "--",
        str(temp_json),
        str(output_blend),
    ]


    subprocess.run(cmd, check=True)
