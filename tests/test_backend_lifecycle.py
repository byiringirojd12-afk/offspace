import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_backend_entrypoint_has_port_8000():
    source = (Path(__file__).parents[1] / "backend" / "main.py").read_text(encoding="utf-8")
    assert 'host: str = "127.0.0.1"' in source
    assert "port: int = 8000" in source


def test_no_duplicate_backend_process_when_health_is_ready():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    assert "if Self::is_ready()" in manager
    assert "BackendState::External" in manager
    assert "process.lock().unwrap().take()" in manager


def test_backend_failure_has_error_message():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    app = (Path(__file__).parents[1] / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "Unable to start OFFSPACE backend" in manager
    assert "did not become ready" in app


def test_packaged_backend_is_resolved_as_a_tauri_resource():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    config = (Path(__file__).parents[1] / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8")
    assert 'resolve("offspace-backend.exe", tauri::path::BaseDirectory::Resource)' in manager
    assert '"binaries/offspace-backend.exe": "offspace-backend.exe"' in config


def test_backend_uses_the_settings_database_environment_variable():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    assert manager.count('"OFFSPACE_DATABASE_URL"') == 2
    assert '"DATABASE_URL"' not in manager


def test_release_backend_does_not_fall_back_to_source_checkout():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    assert '#[cfg(not(debug_assertions))]' in manager
    assert "The packaged OFFSPACE backend resource is missing" in manager


def test_backend_readiness_checks_health_response():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    assert 'GET /api/v1/health HTTP/1.1' in manager
    assert "serde_json::from_str::<HealthResponse>" in manager
    assert 'health.database == "connected"' in manager


def test_supervisor_disables_uvicorn_reloader():
    source = (Path(__file__).parents[1] / "backend" / "main.py").read_text(encoding="utf-8")
    assert "reload=False" in source


def test_cleanup_terminates_owned_process_tree():
    manager = (Path(__file__).parents[1] / "src-tauri" / "src" / "backend_manager.rs").read_text(encoding="utf-8")
    assert 'args(["/PID"' in manager
    assert '"/T", "/F"' in manager


def test_frontend_waits_for_backend_health():
    source = (Path(__file__).parents[1] / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "http://127.0.0.1:8000/api/v1/health" in source
    assert "waitForBackend" in source
    assert "did not become ready" in source


def test_backend_database_url_prefers_tauri_path_and_keeps_legacy_fallback(tmp_path):
    env = os.environ.copy()
    for key in (
        "DATABASE_URL",
        "OFFSPACE_DATABASE_URL",
        "OPENAI_API_KEY",
        "OFFSPACE_OPENAI_API_KEY",
        "OFFSPACE_SECRET_KEY",
        "JWT_SECRET_KEY",
    ):
        env.pop(key, None)

    packaged_url = f"sqlite:///{tmp_path.as_posix()}/packaged.db"
    legacy_url = f"sqlite:///{tmp_path.as_posix()}/legacy.db"
    env["OFFSPACE_DATABASE_URL"] = packaged_url
    env["DATABASE_URL"] = legacy_url
    command = [
        sys.executable,
        "-c",
        "from backend.database.session import DATABASE_URL; print(DATABASE_URL)",
    ]

    preferred = subprocess.run(
        command,
        cwd=Path(__file__).parents[1],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert preferred.stdout.strip() == packaged_url

    env.pop("OFFSPACE_DATABASE_URL")
    fallback = subprocess.run(
        command,
        cwd=Path(__file__).parents[1],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert fallback.stdout.strip() == legacy_url


def test_backend_stdin_shutdown_runs_fastapi_lifespan(tmp_path):
    repository_root = Path(__file__).parents[1]
    port = find_free_port()
    env = os.environ.copy()
    for key in (
        "DATABASE_URL",
        "OFFSPACE_DATABASE_URL",
        "OPENAI_API_KEY",
        "OFFSPACE_OPENAI_API_KEY",
        "OFFSPACE_SECRET_KEY",
        "JWT_SECRET_KEY",
    ):
        env.pop(key, None)
    test_database = tmp_path / "lifecycle.db"
    test_database_url = f"sqlite:///{test_database.as_posix()}"
    env["OFFSPACE_DATABASE_URL"] = test_database_url
    env["DATABASE_URL"] = test_database_url
    log_path = tmp_path / "backend.log"

    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                (
                    "from backend.main import run_server; "
                    f"run_server(host='127.0.0.1', port={port})"
                ),
            ],
            cwd=repository_root,
            env=env,
            stdin=subprocess.PIPE,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )

    try:
        deadline = time.monotonic() + 35
        response_status = None
        while time.monotonic() < deadline and process.poll() is None:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{port}/api/v1/health", timeout=0.5
                ) as response:
                    response_status = response.status
                    break
            except (OSError, urllib.error.URLError):
                time.sleep(0.1)

        if response_status is None:
            if process.poll() is None and process.stdin is not None:
                process.stdin.write("OFFSPACE_SHUTDOWN\n")
                process.stdin.flush()
                process.stdin.close()
            process.wait(timeout=10)
            output = log_path.read_text(encoding="utf-8")
            assert False, f"backend did not become ready; process output:\n{output}"
        assert response_status == 200
        assert process.stdin is not None
        process.stdin.write("OFFSPACE_SHUTDOWN\n")
        process.stdin.flush()
        process.stdin.close()
        process.wait(timeout=10)
        output = log_path.read_text(encoding="utf-8")

        assert process.returncode == 0
        assert "Shutting down Offspace backend" in output
    finally:
        if process.poll() is None:
            if process.stdin is not None and not process.stdin.closed:
                process.stdin.write("OFFSPACE_SHUTDOWN\n")
                process.stdin.flush()
                process.stdin.close()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
