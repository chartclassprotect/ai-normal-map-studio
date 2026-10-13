# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.4.x   | yes       |
| 0.3.x   | security only |
| < 0.3   | no        |

## Reporting a vulnerability

Do **not** open a public issue for security problems. Email
`security@ai-normal-map-studio.dev` with:

- A description of the issue.
- Steps to reproduce.
- The affected module (e.g. `services/onnx_runtime.py`).

We aim to acknowledge within 72 hours and ship a patch within 14 days.

## Threat model

This is a local desktop tool. Attack surface:

- Untrusted image files parsed by `handlers/image_ingest.py`.
- Untrusted `.onnx` model files loaded by `services/onnx_runtime.py`.
- The optional local HTTP bridge in `services/bridge_server.py`.

Never load a model from an untrusted source. The bridge binds to
`127.0.0.1` only; do not expose it to a network.