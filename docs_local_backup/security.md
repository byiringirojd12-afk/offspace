# Offspace Security

## Current Security Posture
- Uses local SQLite storage for memory and preferences.
- Permission gating exists for dangerous automation actions.
- Environment variables are used for API keys.
- No authentication backend or secure session management exists yet.

## Strengths
- Local-first architecture limits remote exposure.
- Dangerous actions require explicit confirmation.
- Memory persistence is encapsulated in a dedicated manager.

## Risks
- `pyttsx3` and `speech_recognition` dependencies are not hardened for production.
- API keys are not encrypted at rest.
- No user accounts, so device-level access is the only control.
- Agent delegation and tool execution are not sandboxed.
- Tauri permissions are broad in config and require review.

## Recommended Improvements
1. Encrypt secrets in `.env` and local storage.
2. Add a secure auth backend for email/Google login.
3. Implement role-based permission checks and user consent dialogs.
4. Harden Tauri manifest permissions to minimum required set.
5. Add audit logs for all automation and AI requests.
6. Validate all user-provided shell/file commands before execution.
