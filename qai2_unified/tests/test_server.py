"""Unit tests for qai2_unified.orchestration.server."""

import json
import threading
import unittest
import urllib.error
import urllib.request

from qai2_unified.orchestration.server import make_server


def _get(url: str) -> tuple[int, dict]:
    with urllib.request.urlopen(url) as resp:
        return resp.status, json.loads(resp.read())


def _post(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


class ServerTest(unittest.TestCase):
    """Integration tests that spin up the stdlib server in a daemon thread."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = make_server("127.0.0.1", 0)  # port 0 → OS picks a free port
        cls.port = cls.server.server_address[1]
        cls.base = f"http://127.0.0.1:{cls.port}"
        t = threading.Thread(target=cls.server.serve_forever, daemon=True)
        t.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    # ------------------------------------------------------------------
    # /health
    # ------------------------------------------------------------------

    def test_health_returns_ok(self) -> None:
        status, body = _get(f"{self.base}/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertIn("version", body)

    def test_health_version_is_string(self) -> None:
        _, body = _get(f"{self.base}/health")
        self.assertIsInstance(body["version"], str)

    # ------------------------------------------------------------------
    # /cycle
    # ------------------------------------------------------------------

    def test_cycle_returns_iteration(self) -> None:
        status, body = _post(f"{self.base}/cycle", {"seed": [1, 0, 1, 0]})
        self.assertEqual(status, 200)
        self.assertIn("iteration", body)
        self.assertIsInstance(body["iteration"], int)

    def test_cycle_iteration_increments(self) -> None:
        _, first = _post(f"{self.base}/cycle", {"seed": [0, 1]})
        _, second = _post(f"{self.base}/cycle", {"seed": [1, 0]})
        self.assertGreater(second["iteration"], first["iteration"])

    def test_cycle_missing_seed_returns_400(self) -> None:
        status, body = _post(f"{self.base}/cycle", {"not_seed": []})
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_cycle_invalid_seed_type_returns_400(self) -> None:
        status, body = _post(f"{self.base}/cycle", {"seed": "not-a-list"})
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_cycle_accepts_float_seed_values(self) -> None:
        status, _ = _post(f"{self.base}/cycle", {"seed": [0.9, 0.1, 1.0]})
        self.assertEqual(status, 200)

    # ------------------------------------------------------------------
    # Unknown routes
    # ------------------------------------------------------------------

    def test_unknown_get_returns_404(self) -> None:
        try:
            urllib.request.urlopen(f"{self.base}/unknown")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)
        else:
            self.fail("Expected HTTPError 404")

    def test_unknown_post_returns_404(self) -> None:
        status, body = _post(f"{self.base}/unknown", {})
        self.assertEqual(status, 404)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
