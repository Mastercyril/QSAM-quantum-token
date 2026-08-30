"""
qai2_unified/orchestration/server.py
--------------------------------------
Minimal stdlib HTTP server that exposes QAI2UnifiedOrchestrator over HTTP so
that external clients (Next.js UI, Puter workers, CLI tools) can trigger
evolution cycles without a direct Python import.

Endpoints
---------
GET  /health       → 200 {"status": "ok", "version": "<runtime_version>"}
POST /cycle        → 200 {"iteration": N, ...}   body: {"seed": [0,1,0,...]}
                      400 if body is missing or seed is not a list of ints

Usage
-----
  # Start on default port 8000:
  python -m qai2_unified.orchestration.server

  # Custom port:
  python -m qai2_unified.orchestration.server --port 9090

  # Bind to all interfaces (e.g. Docker):
  python -m qai2_unified.orchestration.server --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from qai2_unified.orchestration.api import UnifiedOrchestrator

_orchestrator = UnifiedOrchestrator()
_lock = threading.Lock()


class _Handler(BaseHTTPRequestHandler):
    """Request handler for the QAI2 orchestration HTTP server."""

    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D401
        # Delegate to stderr to keep stdout clean for JSON output redirection.
        sys.stderr.write(f"[qai2-server] {fmt % args}\n")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _send_json(self, status: int, payload: Dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> Dict | None:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return None
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Route dispatch
    # ------------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            contract = _orchestrator.runtime.contract
            self._send_json(200, {"status": "ok", "version": contract.version.value})
        else:
            self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/cycle":
            body = self._read_json_body()
            if body is None or "seed" not in body:
                self._send_json(400, {"error": "body must be JSON with a 'seed' list of ints"})
                return
            seed = body["seed"]
            if not isinstance(seed, list) or not all(isinstance(b, (int, float)) for b in seed):
                self._send_json(400, {"error": "'seed' must be a list of numbers"})
                return
            with _lock:
                result = _orchestrator.run_cycle([int(b) for b in seed])
            self._send_json(200, result)
        else:
            self._send_json(404, {"error": "not_found"})


def make_server(host: str = "127.0.0.1", port: int = 8000) -> HTTPServer:
    """Create and return a configured HTTPServer (does not start it)."""
    return HTTPServer((host, port), _Handler)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="QAI2 Unified orchestration HTTP server."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    args = parser.parse_args()

    server = make_server(args.host, args.port)
    sys.stderr.write(f"[qai2-server] Listening on http://{args.host}:{args.port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("[qai2-server] Shutting down.\n")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
