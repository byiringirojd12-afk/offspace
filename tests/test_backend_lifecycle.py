import socket
import subprocess
import sys
from pathlib import Path


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_backend_entrypoint_has_port_8000():
    source = (Path(__file__).parents[1] / "backend" / "main.py").read_text(encoding="utf-8")
    assert 'host="127.0.0.1"' in source
    assert "port=8000" in source


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
    assert 'response.contains("\\\"status\\\":\\\"online\\\"")' in manager


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
