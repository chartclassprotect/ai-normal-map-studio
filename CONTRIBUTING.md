# Contributing to ai-normal-map-studio

Thanks for wanting to help build the AI normal map generator. This project
turns height/diffuse/albedo maps into tangent-space normal maps using a
pipeline of ingest handlers, processors, and output drivers.

## Ground rules

- Python 3.11+ is the reference runtime. C++/CUDA kernels live under
  `services/kernels/` and are built via CMake.
- Every processor must be a pure function of its input job. No global state.
- New handlers register themselves in `handlers/registry.py`.
- Keep tensor shapes documented in the docstring of every processor.

## Dev setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest tests/
```

## Pipeline conventions

A **job** flows: `ingest -> normalize -> infer -> postprocess -> write`.
Each stage is a worker that consumes a `JobContext` and returns a
`JobContext`. Workers never touch the filesystem directly; they use
`utils/io_drivers.py`.

## Pull requests

- One processor per PR where possible.
- Include a golden-image test under `tests/` if you change inference.
- Run `ruff` and `mypy` before opening.

## Reporting issues

Open an issue with the input map, the expected normal, and your
`config/pipeline.yaml`. Attach the job id printed by the CLI.