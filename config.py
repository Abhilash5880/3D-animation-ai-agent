# config.py
from pathlib import Path

# ---- SET THIS TO YOUR ACTUAL BLENDER EXE ON WINDOWS ----
# The full executable path must include blender.exe:
BLENDER_PATH = r"B:\Blender LTS 4.5\blender.exe"

# Path to the blender script used by the bridge (relative path from repo root is fine)
BLENDER_SCRIPT = "blender/scripts/apply_animation.py"

# Output folders (created automatically)
ROOT = Path(__file__).parent.resolve()
OUTPUTS_DIR = ROOT / "outputs"
TIMELINES_DIR = OUTPUTS_DIR / "timelines"
BLENDS_DIR = OUTPUTS_DIR / "blends"

TIMELINES_DIR.mkdir(parents=True, exist_ok=True)
BLENDS_DIR.mkdir(parents=True, exist_ok=True)
