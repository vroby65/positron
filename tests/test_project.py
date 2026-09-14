import ast
import base64
import io
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    loader = SourceFileLoader(f"test_{name}", str(ROOT / name))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


def embedded_file(bundle, filename):
    tree = ast.parse(bundle.read_text(encoding="utf-8"), filename=str(bundle))
    payload = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "PAYLOAD_B64" for target in node.targets)
    )
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(payload))) as archive:
        return archive.read(filename)


class BundleTests(unittest.TestCase):
    def test_custom_runner_name_is_stored_as_positron(self):
        make_bundle = load_script("make_bundle")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = root / "custom-runner"
            runner.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
            www = root / "www"
            www.mkdir()
            (www / "index.html").write_text("ok", encoding="utf-8")

            payload = make_bundle.make_payload(runner, www)
            with zipfile.ZipFile(io.BytesIO(base64.b64decode(payload))) as archive:
                self.assertIn("positron", archive.namelist())
                self.assertNotIn("custom-runner", archive.namelist())

    def test_distributed_bundles_contain_current_runner(self):
        current = (ROOT / "positron").read_bytes()
        for name in ("positron-hello", "memory", "memory.py", "memory.pyw"):
            with self.subTest(bundle=name):
                self.assertEqual(embedded_file(ROOT / name, "positron"), current)

        self.assertFalse((ROOT / "positron.tar.xz").exists())


class RunnerTests(unittest.TestCase):
    def test_persistence_setup_retries_when_native_view_is_not_ready(self):
        positron = load_script("positron")
        positron._PERSISTENCE_SETUP_DONE = False

        self.assertFalse(positron._setup_persistence("gtk", object(), Path("profile")))
        self.assertFalse(positron._PERSISTENCE_SETUP_DONE)

    def test_save_file_api_uses_the_native_destination(self):
        positron = load_script("positron")
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "saved.txt"
            with mock.patch.object(positron, "choose_save_as", return_value=destination), \
                 mock.patch.object(positron.webview, "windows", [object()]):
                result = positron.Api().save_file("suggested.txt", "hello")

            self.assertEqual(destination.read_text(encoding="utf-8"), "hello")
            self.assertEqual(result, f"Saved to {destination}")

    def test_positron_debug_environment_variable_is_honored(self):
        positron = load_script("positron")

        class Server:
            def shutdown(self):
                pass

            def server_close(self):
                pass

        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(positron.sys, "argv", ["positron"]), \
             mock.patch.object(positron.Path, "home", return_value=Path(tmp)), \
             mock.patch.object(positron, "start_http_server", return_value=Server()), \
             mock.patch.object(positron, "wait_for_server", return_value=True), \
             mock.patch.object(positron, "detect_download_dir", return_value=Path(tmp) / "downloads"), \
             mock.patch.object(positron.webview, "create_window", return_value=object()), \
             mock.patch.object(positron.webview, "start") as start, \
             mock.patch.dict(os.environ, {"POSITRON_DEBUG": "1"}, clear=False):
            positron.main()

        self.assertTrue(start.call_args.kwargs["debug"])

    @unittest.skipUnless(shutil.which("npm"), "npm is required for the React integration test")
    def test_react_server_url_is_read_and_process_is_stopped(self):
        positron = load_script("positron")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "node_modules").mkdir()
            (root / "package.json").write_text(
                '{"scripts":{"dev":"node -e \\\"const s=require(\'http\').createServer((q,r)=>r.end(\'ok\'));s.listen(0,\'127.0.0.1\',()=>console.log(\'Local: http://127.0.0.1:\'+s.address().port))\\\""}}',
                encoding="utf-8",
            )

            process, url = positron.start_react_server(root, timeout=10)
            try:
                self.assertRegex(url, r"^http://127\.0\.0\.1:\d+$")
                self.assertIsNone(process.poll())
            finally:
                positron.stop_process(process)

            self.assertIsNotNone(process.poll())
            port = int(url.rsplit(":", 1)[1])
            self.assertFalse(positron.server_is_reachable("127.0.0.1", port))


class ProjectConsistencyTests(unittest.TestCase):
    def test_entrypoints_referenced_by_setup_exist(self):
        install = (ROOT / "install").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("python positron", install)
        self.assertNotIn("python3 positron.py", install)
        self.assertNotIn("make_bundle.py", readme)

    def test_memory_reset_and_tile_geometry(self):
        html = (ROOT / "www" / "index.html").read_text(encoding="utf-8")
        self.assertIn("function resetBestScore()", html)
        self.assertIn("bestScore = 99999999;", html)
        self.assertNotIn("tileWidth + gap", html)
        self.assertNotIn("tileHeight + gap", html)

    def test_license_and_permissions(self):
        self.assertIn("MIT License", (ROOT / "LICENSE").read_text(encoding="utf-8"))
        for name in ("README.md", "install", "make_bundle", "positron", "requirements.txt"):
            with self.subTest(path=name):
                self.assertEqual((ROOT / name).stat().st_mode & 0o022, 0)


if __name__ == "__main__":
    unittest.main()
