# OFFSPACE Architecture and Data Flow

This document separates the **current implementation** from the **approved target workflow**. The target is not yet implemented. Windows 11 is the initial release platform; Linux follows after Windows acceptance.

## Current packaged application

### Startup and shutdown

1. `src-tauri/src/main.rs` creates and manages `BackendManager`.
2. `BackendManager` checks `127.0.0.1:8000` for an OFFSPACE health response. If none is ready, it resolves the packaged `offspace-backend.exe` resource and starts it.
3. The packaged entrypoint is `scripts/backend_entry.py`, which calls `run_server()` in `backend.main`.
4. The child process uses `%LOCALAPPDATA%\Offspace` as its working directory, receives `OFFSPACE_DATABASE_URL`, and writes stdout/stderr to `backend.log`.
5. A Tauri close/exit event calls `BackendManager.stop()` for the owned child. It sends `OFFSPACE_SHUTDOWN` over the child stdin and waits five seconds for FastAPI/Uvicorn lifespan shutdown. If exit is not confirmed, it force-terminates only the owned process tree and logs the result. Source-level tests passed; installed MSI shutdown remains unverified.

### Active FastAPI and chat flow

The packaged `backend.main` constructs the active FastAPI application and registers `backend.api.router`. The active routes are:

- `/api/v1/health`
- `/api/v1/users` — registration, login, and profile
- `/api/v1/settings`
- `/api/v1/memory`
- `/api/v1/chat/message`
- `/api/v1/agents`

React in `src/App.tsx` calls this API directly over `http://127.0.0.1:8000`. The chat path is:

```text
React sign-in → users controller/service → JWT
React send → authenticated chat controller → ChatService
           → provider preference/requested provider → ModelRouter
           → OpenAIProvider or LocalModelProvider (Ollama)
           → persist user and assistant ConversationEntry rows
           → response to React
```

The model receives the current prompt, not retrieved conversation history. Conversation rows are written on success, but the active UI/API does not load them into a later session. Settings and SQL memory routes use the same SQLAlchemy database models.

The engine in `backend/database/session.py` prefers `OFFSPACE_DATABASE_URL`, retains `DATABASE_URL` as a compatibility fallback, then falls back to `sqlite:///./offspace.db` for source development. Tauri sets `OFFSPACE_DATABASE_URL` to `%LOCALAPPDATA%\Offspace\offspace.db` for packaged execution. No database migration or existing-user-data change is performed.

## Parallel and legacy implementations

- Root `main.py` is a separate interactive CLI using `core.Assistant`; it is not the packaged FastAPI entrypoint.
- `backend/api/main.py` constructs a second FastAPI app with different routes. Its AI route is a 501 placeholder; it is not registered by `backend.main`.
- The desktop API's SQLAlchemy `MemoryEntry` is distinct from root `memory.MemoryManager` (`.offspace/memory.db`) and `backend.memory.MemoryDatabase` (`data/offspace_memory.db`).
- `backend.knowledge.KnowledgeManager` is not wired to active API/chat. Its embedder produces a length-based placeholder vector and its vector store is in-memory substring matching.
- The registered agent service persists pending task records but does not dispatch them. Specialist agent classes and brain/orchestrator modules are not called from the active chat path.
- React voice uses browser SpeechRecognition/SpeechSynthesis after a user click. Wake-phrase detection updates UI state and the prompt field; sending still requires the separate Send action. The CLI has a separate Python voice path.
- Automation, workflow approval, tool, and audit implementations are separate legacy modules, not a supported active API workflow.

## Approved target workflow

Preserve the current Tauri/React, FastAPI, SQLAlchemy, OpenAI, and Ollama interfaces where practical. The desired request lifecycle is:

```text
React/Tauri
  → authenticated FastAPI route
  → Assistant Orchestrator
  → context and intent resolution
  → Model Router or supported specialist agent
  → Approval Manager for sensitive actions
  → validated tool execution
  → result verification and audit event
  → response and persisted conversation
```

Ordinary chat and local/cloud provider selection must not silently turn into tool execution. A local-first request must not be sent to OpenAI without an explicit user choice. Sensitive tool actions require a visible, action-specific approval; no permission request may be auto-approved.

## Migration and sequencing constraints

1. Complete installed Windows app shutdown and uninstall verification before changing later workflow layers.
2. Inventory and back up the actual active database before path changes or schema migrations. Do not merge the three memory stores by deleting or overwriting data.
3. Keep the existing authenticated chat/settings/memory routes while establishing a single orchestrator path.
4. Keep shell-based modules isolated until their references are verified and replaced by typed, bounded tools.
5. Add semantic knowledge and agents only through the same file-permission, approval, and audit boundaries.
6. Validate installed voice behavior on available hardware; do not claim success from UI state alone.
7. Complete Windows acceptance before Linux release work.

See [MVP_AUDIT.md](./MVP_AUDIT.md) for verified gaps and [security.md](./security.md) for security-specific constraints.
