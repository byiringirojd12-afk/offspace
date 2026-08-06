# Developer Guide

## Project Structure
- `main.py` - Entry point for the Python assistant.
- `core/` - Assistant orchestration, voice, automation, security, and routing.
- `memory/` - Local SQLite memory manager.
- `backend/` - AI provider, knowledge, agent collaboration, and tool scaffolding.
- `src/` - React UI for Tauri desktop.
- `src-tauri/` - Tauri native configuration and Rust bridge.
- `tests/` - Python unit tests.

## Development Workflow
1. Activate Python environment.
2. Install Python dependencies.
3. Install frontend dependencies.
4. Run backend and frontend in parallel for development.

## Running Tests
```bash
.venv\Scripts\python.exe -m pytest -q
```

## Adding Providers
- Update `backend.intelligence.provider` with new provider classes.
- Add provider mapping in `backend.intelligence.router.ModelRouter`.
- Implement environment-based configuration and fallback logic.

## Adding a Tool
1. Add a new tool class in `backend.tools` implementing `ToolInterface`.
2. Register the tool in a central registry.
3. Add safety validation and permission checks.

## Deploying Desktop Builds
- Use Tauri commands once the frontend is built.
- Use `npm run build` and then `npm run tauri build`.
- Ensure the bundle configuration in `src-tauri/tauri.conf.json` is updated for production.
