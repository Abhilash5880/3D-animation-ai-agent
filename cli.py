import sys
from pathlib import Path
from rich import print

from agent.prompt_parser import parse_prompt
from agent.action_planner import build_timeline
from blender.run_blender import run_blender


def main():
    if len(sys.argv) < 2:
        print("[red]Error:[/red] Please provide an animation prompt.")
        print('Example: python cli.py "make the character wave"')
        sys.exit(1)

    prompt = sys.argv[1]

    print("[bold green]AI Animation Agent[/bold green]")
    print(f"[cyan]Prompt received:[/cyan] {prompt}")

    plan = parse_prompt(prompt)
    print("[bold green]Generated Animation Plan:[/bold green]")
    print(plan.model_dump_json(indent=2))

    timeline = build_timeline(plan)
    print("[bold green]Generated Timeline:[/bold green]")
    print(timeline.model_dump_json(indent=2))

    output_dir = Path("outputs/blends")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_blend = output_dir / "test_animation.blend"

    print("[yellow]Launching Blender (headless)...[/yellow]")
    run_blender(animation_timeline=timeline, output_blend=output_blend)

    print(f"[bold green]Blend file generated at:[/bold green] {output_blend}")


if __name__ == "__main__":
    main()
