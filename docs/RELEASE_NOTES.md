# OFFSPACE MVP Release Notes

## Included

- FastAPI backend with authentication and SQLAlchemy persistence
- OpenAI and Ollama-compatible provider routing
- Persistent memory and user settings
- Existing voice, automation and desktop interface
- Tauri-owned local backend startup and loopback readiness
- Windows executable build

## Known limitations

- The Windows NSIS/MSI installer was not generated because required network downloads failed.
- Live OpenAI and Ollama responses are unverified in this environment.
- Real microphone/wake/TTS hardware validation is incomplete.
- Linux/WSL validation is unavailable.
- A valid API key or local Ollama server is required for live AI responses.
