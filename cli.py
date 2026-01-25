# cli.py
import sys
from pathlib import Path
from rich import print

from agent.prompt_parser import parse_prompt
from agent.action_planner import build_timeline
from blender.run_blender import run_blender

def main():
    if len(sys.argv) < 3:
        print("[red]Error:[/red] Please provide an animation prompt and a model path.")
        print('Example: python cli.py "make the character wave and jump" assets/models/Remy.fbx')
        sys.exit(1)

    prompt = sys.argv[1]
    model_path = Path(sys.argv[2])
    if not model_path.exists():
        print(f"[red]Error:[/red] Model not found: {model_path}")
        sys.exit(1)

    print("[bold green]AI Animation Agent[/bold green]")
    print(f"[cyan]Prompt received:[/cyan] {prompt}")
    print(f"[cyan]Model path:[/cyan] {model_path}")

    plan = parse_prompt(prompt)
    print("[bold green]Generated Animation Plan:[/bold green]")
    print(plan.model_dump_json(indent=2))

    timeline = build_timeline(plan)
    print("[bold green]Generated Timeline:[/bold green]")
    print(timeline.model_dump_json(indent=2))

    output_dir = Path("outputs/blends")
    output_dir.mkdir(parents=True, exist_ok=True)

    # output filename includes model name
    safe_name = model_path.stem.replace(" ", "_")
    output_blend = output_dir / f"{safe_name}_animated.blend"

    print("[yellow]Launching Blender (headless)...[/yellow]")
    run_blender(animation_timeline=timeline, model_path=model_path, output_blend=output_blend)

    print(f"[bold green]Blend file generated at:[/bold green] {output_blend}")

if __name__ == "__main__":
    main()
