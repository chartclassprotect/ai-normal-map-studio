"""Typer CLI for ai-normal-map-studio.

Commands:
    generate   Run the full pipeline on one or more input maps.
    batch      Run a directory of maps through the pipeline.
    inspect    Dump the resolved job context without running inference.
    models     List registered models from config/models.yaml.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ai_normal_map_studio.bootstrap import build_pipeline
from ai_normal_map_studio.utils.job_context import JobContext

app = typer.Typer(
    add_completion=False,
    help="AI normal map generator — height/diffuse/albedo to tangent-space normal.",
)
console = Console()


@app.command()
def generate(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    output_dir: Path = typer.Option(Path("outputs"), "--out", "-o"),
    config: Path = typer.Option(Path("config/pipeline.yaml"), "--config", "-c"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    flip_green: bool = typer.Option(False, "--flip-green"),
) -> None:
    """Generate a normal map from a single input image."""
    pipeline = build_pipeline(config)
    job = JobContext(
        input_path=input_path,
        output_dir=output_dir,
        model_override=model,
        flip_green=flip_green,
    )
    result = pipeline.run(job)
    console.print(f"[green]done[/] -> {result.output_path}")


@app.command()
def batch(
    input_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    output_dir: Path = typer.Option(Path("outputs"), "--out", "-o"),
    config: Path = typer.Option(Path("config/pipeline.yaml"), "--config", "-c"),
    pattern: str = typer.Option("*.png", "--pattern", "-p"),
) -> None:
    """Run every matching file in a directory through the pipeline."""
    pipeline = build_pipeline(config)
    files = sorted(input_dir.glob(pattern))
    if not files:
        console.print("[yellow]no files matched[/]")
        raise typer.Exit(code=1)
    for f in files:
        job = JobContext(input_path=f, output_dir=output_dir)
        result = pipeline.run(job)
        console.print(f"[green]{f.name}[/] -> {result.output_path}")


@app.command()
def inspect(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    config: Path = typer.Option(Path("config/pipeline.yaml"), "--config", "-c"),
) -> None:
    """Print the resolved job context without running inference."""
    from ai_normal_map_studio.utils.config_loader import load_pipeline_config

    cfg = load_pipeline_config(config)
    console.print_json(data={"input": str(input_path), "config": cfg})


@app.command()
def models(
    registry: Path = typer.Option(Path("config/models.yaml"), "--registry", "-r"),
) -> None:
    """List registered models."""
    from ai_normal_map_studio.utils.config_loader import load_model_registry

    for name, spec in load_model_registry(registry).items():
        console.print(f"[cyan]{name}[/]  {spec['path']}  ({spec.get('license', 'unknown')})")


if __name__ == "__main__":
    app()