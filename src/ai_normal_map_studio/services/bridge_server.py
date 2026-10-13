"""Local HTTP bridge.

Exposes `POST /generate` on 127.0.0.1 so external tools (Blender addon,
Substance plugin) can call the pipeline. Binds to loopback only.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from ai_normal_map_studio.bootstrap import build_pipeline
from ai_normal_map_studio.utils.job_context import JobContext


class _Handler(BaseHTTPRequestHandler):
    pipeline = None  # set by serve()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/generate":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length) or b"{}")
        job = JobContext(
            input_path=Path(body["input"]),
            output_dir=Path(body.get("out", "outputs")),
        )
        result = self.pipeline.run(job)
        payload = json.dumps({"output": str(result.output_path)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args) -> None:  # silence default logger
        return


def serve(port: int = 8765, config: Path = Path("config/pipeline.yaml")) -> None:
    _Handler.pipeline = build_pipeline(config)
    httpd = HTTPServer(("127.0.0.1", port), _Handler)
    httpd.serve_forever()