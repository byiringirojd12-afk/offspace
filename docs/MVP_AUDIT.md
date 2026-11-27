# OFFSPACE Local MVP Audit

**Inspection date:** 2026-11-27
**Platform:** Windows 11, build 26300
**Branch / commit:** `mvp-audit-development` / `d5419b0d28603a999299fe8a2c70257763db0e2a`

This audit describes the local worktree, not just the branch commit. No application code was changed during this inspection.

## Local worktree and release state

- The working tree has existing changes in `MVP_RELEASE_REPORT.md`, `docs/WINDOWS_INSTALLATION.md`, and `src-tauri/tauri.conf.json`. The Tauri config change references the existing ICO needed by the MSI bundler.
- Git also reports `src-tauri/Cargo.toml` and tracked `src-tauri/target/debug` outputs modified, including incremental files deleted. No textual diff was visible for `Cargo.toml`; these files were preserved. No untracked Git files were reported.
- The MSI exists at `C:\Temp\offspace-release-target\release\bundle\msi\Offspace Desktop_0.1.0_x64_en-US.msi` (32,157,696 bytes). It is unsigned. The per-machine installation remains under `C:\Program Files\Offspace Desktop`.
- The installed backend health endpoint currently responds with `{"status":"online","database":"connected","version":"1.0.0"}`. The app remains running; installed-app shutdown and uninstall have not been verified because the user could not close the native window. No process-kill workaround or uninstall was attempted.
- Existing MSI packaging evidence shows the desktop executable and backend sidecar are included and their installed hashes match the release binaries. The installation was not isolated from the normal user app-data environment.

## Baseline checks

| Check | Result |
|---|---|
| Python | **PASS** — project `.venv` Python 3.14.6: 39 tests passed, with one existing `PytestReturnNotNoneWarning` from the hardware-device enumeration diagnostic. |
| Frontend | **PASS** — `npm run build`; TypeScript and Vite production build succeeded. |
| Rust | **PASS** — `cargo check` succeeded; `cargo test` passed 2 lifecycle readiness tests, using `CARGO_TARGET_DIR=C:\Temp\offspace-release-target`. |
| Packaged backend | **PARTIAL PASS** — installed health and database connectivity respond; installed shutdown remains unverified. |
| Packaging | **PASS WITH BLOCKERS** — existing WiX 3.14.1 MSI artifact and installed payload verified; MSI is unsigned and emitted WiX ICE warnings. No packaging rebuild was run because it would replace the existing MSI. |
| User app database | **NOT READ** — `%LOCALAPPDATA%\Offspace\offspace.db` metadata remained 40,960 bytes with its prior timestamp in the last check; this is not proof that no writes occurred. The backend log grew during health checks. |

### Test-data incident and preservation

The full Python suite includes an Assistant test that constructs the legacy `core.Assistant`; its default memory manager writes to the ignored repository file `.offspace/memory.db`. The file was observed after the test at 28,672 bytes. No pre-test metadata was captured, so whether it existed before the test and what changed cannot be determined. Its contents were not read. After the user's approval, a copy of the current post-test file was saved to `C:\Temp\offspace-baseline-backup-20261127-1116\memory.db`; the original was not altered by the backup. Do not rerun that test against the repository default until its memory path is isolated.

## Current application data flow

1. Tauri starts `offspace-backend.exe` through `src-tauri/src/backend_manager.rs`; the sidecar entrypoint imports `backend.main:app`.
2. `backend.main` registers `backend.api.router`. The registered API provides health, user authentication, memory, chat, agent-task, and settings routes.
3. React in `src/App.tsx` calls the local HTTP API directly. Chat goes through the authenticated chat controller and `ChatService`, then `ModelRouter`, then OpenAI or Ollama.
4. `ChatService` stores successful user/assistant messages in SQLAlchemy `ConversationEntry` rows. The current UI does not load persisted history or send history/context back to the model.
5. Authentication uses password hashing and JWTs. Provider preference, memory entries, and conversations use SQLAlchemy models.

The implemented chat path does **not** currently pass through the `core.Assistant`, the brain/orchestrator modules, specialist agents, approval workflow, tool execution, or a verification stage. `backend/api/main.py` is a second FastAPI app with different routes; it is not the packaged entrypoint, and its AI route returns 501.

## Findings and blockers

1. **Installed lifecycle is the gate.** Startup and health are verified, but the installed window could not be closed, so shutdown and uninstall are not verified. Later architecture work should wait until the installed lifecycle is safely resolved.
2. **Database selection contract is inconsistent.** Tauri sets `OFFSPACE_DATABASE_URL`; `backend/database/session.py` reads `DATABASE_URL` and otherwise uses `sqlite:///./offspace.db`. The packaged sidecar's working directory is the app-data directory, so the default relative path can land there, but an inherited `DATABASE_URL` can redirect it. The reported health response does not prove which file was selected. No path change or migration was attempted.
3. **There are multiple workflows and memory stores.** The root CLI uses `core.Assistant` and `.offspace/memory.db`; the backend also has a separate `backend.memory` SQLite store. The desktop API's SQLAlchemy memory table is the active Tauri memory path. Consolidation needs a data inventory and backups first.
4. **The requested orchestrator flow is not connected.** Chat currently calls the model router directly. Intent/context orchestration, approval, action execution, verification, and response auditing are absent from this path.
5. **Knowledge retrieval is scaffolded.** The knowledge manager uses a placeholder length-based embedding and in-memory substring matching; no active API/chat call site or persistent semantic index was found.
6. **Agent execution is incomplete.** The active agent endpoint creates pending task rows and reads their status; it does not dispatch work. Specialist agent classes return placeholder “ready” results and are not connected to the active chat route.
7. **Approval and automation are not release-ready.** The legacy `core` permission manager's request method automatically sets a permission to true. Separate backend tool modules contain `shell=True` execution and a Windows application launcher that passes a command to a shell. Those modules were not found in the packaged API call path; they must remain isolated until dependency and approval boundaries are redesigned. The legacy file tool also lacks path containment.
8. **Voice is split.** The React UI uses browser Web Speech APIs after a user click; detecting “Hey Offspace” marks status and fills the prompt, but does not itself submit it. The Python CLI has a separate SpeechRecognition/pyttsx3 path. Neither complete installed voice flow nor hardware output is verified.
9. **Production security configuration needs review.** Default CORS origins include development localhost origins, with credentials enabled and methods/headers set to `*`; the Tauri CSP is `null`. The test suite checks the Tauri localhost origin, not a production allow/deny policy. The backend generates a random JWT secret when no configured key is supplied, so persistence across restarts depends on supplying a stable secret.
10. **Release acceptance remains incomplete.** The MSI is unsigned; WiX emitted ICE03/40/57/61 warnings. Installed chat, authentication, user-data preservation under isolated testing, live Ollama/OpenAI inference, and installed shutdown/uninstall remain unverified. No model was downloaded and no credentials were inspected or sent.

## Proposed implementation order

1. Resolve the installed app shutdown safely; then verify the owned sidecar exits and uninstall only the explicitly authorized MSI. Do not force-kill or alter the active database.
2. Before any database-path or schema change, identify the database actually opened by the packaged backend without exposing contents, back it up, and test the explicit path contract in an isolated profile.
3. Establish one active API/chat workflow that preserves current auth, settings, and route contracts; add orchestration/context incrementally rather than replacing working providers.
4. Implement a real approval boundary before any automation/tool invocation. Keep shell-based legacy modules unreachable; replace shell-string execution with narrowly typed, validated operations only after call-site and dependency review.
5. Select one memory store for the active desktop path and migrate legacy data only after user-approved backups and migration tests. Add conversation-history loading/context without losing existing rows.
6. Implement persistent semantic retrieval and connect it only after ingestion scope, file permission, embedding model, and data-retention behavior are agreed.
7. Connect specialist agents through the same approval and audit path; add explicit task lifecycle tests.
8. Validate browser/Python voice behavior on available hardware, preserving “Hey Offspace” and explicit send/approval behavior.
9. Repeat regression and isolated Windows installation/lifecycle tests, sign the installer, review bundler warnings, and defer Linux certification until Windows acceptance passes.

No application-code changes or database migrations were made in this audit. See [architecture.md](./architecture.md), [security.md](./security.md), [WINDOWS_INSTALLATION.md](./WINDOWS_INSTALLATION.md), and [MVP_RELEASE_REPORT.md](../MVP_RELEASE_REPORT.md).
