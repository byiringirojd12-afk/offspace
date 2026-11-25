# OFFSPACE Windows MVP Release Validation

## Summary

Validation continued on branch `mvp-audit-development`; no commits or pushes were created. The existing app data directory was used for the desktop startup test, but no account or memory records were created or edited. The Tauri release executable and backend integration now pass direct launch checks. Installer generation remains blocked by Tauri's NSIS dependency download. OFFSPACE is **not ready for distribution**.

## Backend integration and packaging

- **PASS — Backend sidecar build:** `scripts/build_backend.mjs` produced `src-tauri\binaries\offspace-backend.exe` with Python 3.12.10 and PyInstaller 6.15.0. The backend runtime requirements now declare `PyJWT` and `bcrypt`, which were missing from the first sidecar and prevented authentication from loading.
- **PASS — Sidecar API smoke test:** using a newly created temporary SQLite database, the packaged backend returned a healthy response and completed registration, login, authenticated memory save, and memory search. The smoke test did not access the user's `%LOCALAPPDATA%\Offspace\offspace.db`.
- **PASS — Readiness checks:** Rust tests verify that readiness requires the OFFSPACE health response and rejects an unrelated HTTP listener. `cargo test` passed both tests.
- **PASS — Database configuration correction:** Tauri now passes `OFFSPACE_DATABASE_URL`, matching the settings environment prefix. This keeps packaged data in the configured application data directory rather than relying on a checkout-relative database.
- **PASS — Tauri-managed sidecar startup and frontend connection:** launched the freshly built release executable at `C:\Temp\offspace-release-target\release\offspace-desktop.exe`. Its packaged sidecar started from the same release directory; the UI displayed “Backend connected. System ready.” and `GET /api/v1/health` returned `{"status":"online","version":"1.0.0"}`.
- **PASS — Tauri-owned backend shutdown:** after closing the desktop window, both the desktop and sidecar processes exited, port 8000 was free, and the health endpoint was unavailable.
- **PASS — Startup failure feedback:** launched a temporary copy of the desktop executable without its sidecar. The UI showed “OFFSPACE backend did not become ready” with the backend log location; `backend.log` recorded that the packaged resource was missing. The temporary test copy was removed.
- **PASS — Duplicate-listener check:** the one-file PyInstaller sidecar ran its bootloader/worker process pair, with one worker listening on port 8000. No second backend listener was observed.
- **NOT TESTED — Desktop memory persistence across restart:** authenticated memory save/search passed in the isolated sidecar smoke test and Python workflow tests. I did not write test records to the existing app database, so persistence through a Tauri app restart remains unverified.

## Windows executable and installer

- **PASS — Frontend production build:** `npm run build`.
- **PASS — Rust compile check:** `cargo check --manifest-path src-tauri\Cargo.toml`.
- **PASS — Rust lifecycle tests:** `cargo test --manifest-path src-tauri\Cargo.toml` — 2 passed.
- **PASS — Build-output root cause and recovery:** `CARGO_TARGET_DIR` was unset and no Cargo target-dir config was present. `src-tauri\target` is a Microsoft Cloud Files reparse point inside OneDrive; its release build directories carry the read-only attribute. The current user has ACL Full Control, disk space was ample, and no Cargo/Rust build was active at diagnosis. The `autocfg` build script explicitly rejects a read-only `OUT_DIR`, causing `output path is not a writable directory`. Preserving the original target, the build was redirected per-command to `C:\Temp\offspace-release-target`.
- **PASS — Windows release executable:** Tauri release compilation completed in 19m 11s. Executable: `C:\Temp\offspace-release-target\release\offspace-desktop.exe` (8,436,736 bytes). The packaged sidecar is `C:\Temp\offspace-release-target\release\offspace-backend.exe` (29,793,088 bytes).
- **BLOCKED — Installer generation:** Tauri CLI 2.11.4 reached NSIS verification and attempted its pinned `nsis-3.11.zip` download. The connection to GitHub was forcibly closed (`os error 10054`). The installed NSIS 3.13 compiler did not satisfy Tauri's pinned dependency check. No retry or unsupported local-compiler substitution was attempted.
- **NOT TESTED — Installer installation:** no NSIS bundle directory or installer artifact exists; installation and installed-data persistence cannot be verified.

## AI providers

- **BLOCKED — OpenAI live test:** neither supported key variable nor an OpenAI key in the local `.env` was configured. No live request was made and no credential was printed. Mocked provider tests cover configuration aliases and sanitized error handling; they are not live validation.
- **BLOCKED — Ollama live response:** the local server was reachable, but reported zero available models. No model was downloaded and no real completion was generated. To retry, start Ollama and install the configured model only with the user's approval, for example `ollama pull llama3.2`.

## Voice and hardware

- **PASS — Python 3.12 dependency/import checks:** prior validation confirmed Python 3.12.10 with SpeechRecognition, PyAudio and `aifc`; microphone device enumeration and a `pyttsx3` invocation also completed.
- **FAIL — Prior microphone recognition attempt:** a previously approved capture returned an empty transcript. No successful recognition is claimed, and no new microphone recording or external speech-recognition request was made.
- **NOT TESTED — Wake phrase and desktop voice workflow:** no acoustic wake phrase or complete spoken desktop interaction was verified. TTS engine invocation alone does not establish audible output.
- Python 3.12.10 is the voice-stack version verified in this environment; the project's formal minimum supported Python version has not been established. Python 3.14 compatibility remains unverified.

## Regression results

- **PASS — Python suite:** 39 passed. Pytest reports one existing `PytestReturnNotNoneWarning` from `backend/voice/microphone_test.py`; that diagnostic enumerates devices and is not a recording/recognition test.
- **PASS — Frontend production build:** `npm run build`.
- **PASS — Rust checks:** `cargo check` passed; `cargo test` passed 2 lifecycle readiness tests.
- **PASS — Tauri release compilation:** built with `CARGO_TARGET_DIR=C:\Temp\offspace-release-target`; the subsequent NSIS packaging step failed as described above.
- **PASS — Packaged backend smoke:** health, registration/authentication, memory save/search, and login passed against a disposable database.
- **PASS — Mocked provider, workflow, voice, and automation tests:** covered by the Python suite; these do not substitute for external provider, microphone, or physical automation validation.

## Linux

- **BLOCKED — Linux tests and desktop build:** no Linux environment or CI runner was available for this validation; Linux compatibility is not claimed.

## Remaining blockers and release decision

1. Provide the Tauri-pinned NSIS 3.11 dependency through a working network or an officially supported offline mechanism; do not repeatedly retry the connection-reset download.
2. Generate the installer and test installation and installed-app data persistence. No installer currently exists.
3. Configure an OpenAI key for a real provider request and make an Ollama model available for real local inference.
4. Repeat microphone capture and recognition with authorization; verify wake phrase and audible desktop TTS.
5. Run Linux validation.

**Release decision: NOT READY.** The Tauri executable, packaged sidecar startup/readiness, frontend connection, failure message, and owned-process cleanup were directly verified. However, there is no installer, installed workflow or desktop memory-restart validation; live AI services, hardware voice, and Linux validation also remain incomplete.

## Changes and working-tree note

This continuation diagnosed the OneDrive read-only target issue and used the separate `C:\Temp\offspace-release-target` without changing Cargo configuration or deleting the original target. It built and launched the Tauri release, verified backend startup/readiness/cleanup and startup-failure feedback, reran Python and Rust tests, and updated this report and the Windows installation guide. Other modified and untracked files were preserved. No commit or push was made.
