# Offspace Architecture

## Overview
Offspace is a local-first desktop AI assistant with optional cloud synchronization. It is built as a Tauri desktop application using React for UI and Python for backend AI, voice, memory, and automation.

## System Components

### Desktop Shell
- Tauri hosts the React frontend and manages native desktop integration.
- Supports Windows and Linux now, with macOS readiness via Tauri configuration.
- UI provides voice capture, chat, memory panel, and automation controls.

### AI Engine
- `backend.intelligence` routes provider calls.
- OpenAI provider is implemented; local provider is scaffolded.
- Provider switching is planned via configuration and environment variables.
- Model selection, retries, and fallback behavior are required for production.

### Memory System
- `memory.memory_manager` provides short-term and long-term memory.
- Uses SQLite for persistence in `.offspace/memory.db`.
- Supports saving preferences and simple search.
- Document knowledge graph is scaffolded in `backend.knowledge` and requires full embedding/RAG implementation.

### Agents
- `backend.collaboration.AgentManager` contains named agents.
- Agents are currently simple task reviewers and require production task planning and collaboration.

### Tools and Automation
- `core.automation.AutomationManager` handles file and dangerous actions with permission gating.
- `backend.tools` contains tool interfaces and executors.
- Additional safety, browser automation, and system command execution remain incomplete.

### Voice
- `core.voice.VoiceController` uses `speech_recognition` and `pyttsx3` for runtime voice I/O.
- Whisper/Vosk/Piper are not yet integrated.
- Current implementation is a prototype and needs production-grade audio handling.

## Data Flow
1. User input is captured in the desktop UI or voice system.
2. Assistant routes the command based on intent.
3. Memory system stores conversation context.
4. AI provider generates responses.
5. Automation executes permitted actions.

## Security and Permissions
- `core.security.PermissionManager` stores simple permission flags.
- Dangerous actions require explicit confirmation.
- Fine-grained user permission management and secure storage are not implemented yet.

## Integration Points
- React frontend connects to the Python backend through Tauri commands and HTTP APIs in production.
- AI provider uses environment variables and SDKs.
- Memory storage is local but designed to support sync APIs.

## Gaps for Phase 8
- No authentication or cloud backend.
- No installer or release pipeline defined.
- No monitoring, logging dashboard, or health checks.
- Voice pipeline is incomplete.
- Agent system is prototype-only.
- Desktop shell lacks system tray, startup option, and crash recovery.
