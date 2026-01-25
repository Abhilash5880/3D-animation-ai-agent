# Quick start : Clone, setup, and run (Git Bash on Windows)

Use this file to **clone the repo, set up the Python environment, provide a Mixamo-rigged model, and run the CLI**. All commands below assume **Git Bash** on Windows.


---

## 1. Clone the repository
```bash
git clone "this repo url"
cd 3D-animation-ai-agent
```

## 2. Create and activate the virtual environment (Git Bash)
```bash
python -m venv .venv
source .venv/Scripts/activate
```
## 3. Install Python dependencies
```bash
pip install -r requirements.txt
```
## 4. Configure Blender path

Open config.py in the repo root and set the Blender executable absolute path exactly. Example content:

```bash
BLENDER_PATH = r"C:\Users\--your path--\blender.exe"
BLENDER_SCRIPT = "blender/scripts/apply_animation.py"
```

## 5. Download model

Download a Mixamo-rigged humanoid-type model from Mixamo website. It is peferred because the rigs are converted based on mixamo models in the program(either .fbx or .glb).

And add the model in the below folder.
```bash
assets/models/gltf #for .glb files
or
assets/models/mixamo-fbx #for .fbx files
```

## 6. Run the CLI (produce animated .blend)
```bash
python cli.py "make the character wave and jump" "assets/models/Remy.fbx"
```
The CLI parses the prompt, builds a timeline, launches Blender headless, imports the model, applies procedural animations (or bone transforms if an armature exists), and writes the output .blend.

Expected output file:
```bash
outputs/blends/Remy_animated.blend
```
## 7. Open the generated .blend in Blender GUI
```bash
"C:/Users/--your path--/blender.exe" "outputs/blends/Remy_animated.blend"
```

## Demo videos
#### Demo 1
```
Model: Remy.fbx
prompt: "make the character wave and jump" 
```
output:
[Watch Demo 1](demos/demo1.mp4)

#### Demo 2
```
Model: xchar.glb
prompt: "make the character wave and jump" 
```
output:
[Watch Demo 2](demos/demo2.mp4)

#### Demo 3
```
Model: ychar.glb
prompt: "make the character wave and jump" 
```
output:
[Watch Demo 3](demos/demo3.mp4)

