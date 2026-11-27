# Windows Build and Installation

## Current release status

The Tauri executable and packaged backend were built successfully:

- Executable: `C:\Temp\offspace-release-target\release\offspace-desktop.exe`
- Backend resource: `C:\Temp\offspace-release-target\release\offspace-backend.exe`

The MSI was generated and installed on Windows 11. The installed UI displayed a connected backend and the health endpoint returned online with its database connected. The installed app remains open because the user could not close the native window; installed shutdown and uninstallation have not been verified. The test used the normal user app-data environment rather than an isolated profile. OFFSPACE is **not ready for distribution**.

| Check | Result |
| --- | --- |
| Tauri bundle configuration | **PASS — inspected.** `src-tauri\tauri.conf.json` retains NSIS as its default target, packages `binaries\offspace-backend.exe` as `offspace-backend.exe`, and references the existing `icons\icon.ico` required by MSI bundling. |
| Tauri CLI bundle options | **PASS — inspected.** Installed Tauri CLI 2.11.4 reports `msi` and `nsis` as supported Windows bundle options. |
| NSIS | **NOT USED.** NSIS 3.13 is installed at `C:\Program Files (x86)\NSIS\makensis.exe`, but Tauri pins NSIS 3.11. Its earlier GitHub download failed with `os error 10054`; 3.13 was not substituted and the download was not retried. |
| WiX / MSI | **PASS.** Tauri CLI obtained and checksum-validated its pinned WiX 3.14.1 toolset (`candle`/`light` 3.14.1.8722). |
| Installer artifact | **PASS.** MSI: `C:\Temp\offspace-release-target\release\bundle\msi\Offspace Desktop_0.1.0_x64_en-US.msi`, 32,157,696 bytes. It was generated with `--no-sign` and is unsigned. WiX emitted ICE03, ICE40, ICE57, and ICE61 warnings. |
| Installer payload | **PASS.** Generated WiX source includes the desktop executable, backend sidecar resource, and configured icon. Installed desktop and backend files are present under `C:\Program Files\Offspace Desktop`; their hashes match the release binaries. |
| Installation and launch | **PARTIAL PASS.** Per-machine installation completed at `C:\Program Files\Offspace Desktop`. The installed UI displayed a connected backend; `GET http://127.0.0.1:8000/api/v1/health` returned `{"status":"online","database":"connected","version":"1.0.0"}`. No chat request was sent. |
| Data and lifecycle | **BLOCKED / NOT TESTED.** Testing was not isolated from the user's app-data environment. The database file remained 40,960 bytes with its prior modification time, but its contents were not read; `backend.log` grew during startup and health checks. The user could not close the app, so shutdown and uninstallation were not attempted. The MSI remains installed. |

No pinned dependency was changed. The only packaging configuration change references the existing `src-tauri\icons\icon.ico`, required by the MSI bundler. Do not substitute the installed NSIS 3.13 compiler for the pinned 3.11 dependency or repeatedly retry the failed download.

### Cargo output directory

The earlier `output path is not a writable directory` error was caused by `src-tauri\target` being a Microsoft Cloud Files reparse point under OneDrive. Release build directories there carried the read-only attribute, which `autocfg` rejects for `OUT_DIR`. `CARGO_TARGET_DIR` was unset, no Cargo target-dir configuration was found, the user ACL allowed Full Control, and disk space was sufficient. The original target was preserved. Use a separate target for builds:

```powershell
$env:CARGO_TARGET_DIR = "C:\Temp\offspace-release-target"
```

## Build prerequisites

1. Windows 11.
2. Visual Studio Build Tools 2022 with **Desktop development with C++** (including MSVC and the Windows SDK).
3. Node.js 20 or newer and npm.
4. Rust installed through rustup.
5. Python 3.12 and PyInstaller 6.15.0 for the backend sidecar. Python 3.12.10 was used for the successful sidecar build.
6. For NSIS packaging, make Tauri CLI's pinned NSIS 3.11 dependency available through a supported installation or offline mechanism. The locally installed NSIS 3.13 is not a substitute. MSI packaging succeeded here using Tauri's checksum-pinned WiX 3.14.1 download.
7. WebView2 Runtime on end-user systems, if it is not already present.

From a Visual Studio Developer Command Prompt, verify the compiler and linker:

```bat
cl
link
```

## Build commands

Install project packages and backend requirements in the Python 3.12 environment used for packaging:

```bat
npm install
py -3.12 -m pip install -r requirements.txt -r requirements-packaging.txt
```

Use the same writable target for Cargo and Tauri. If Python 3.12 is not selected by the launcher, set `OFFSPACE_PYTHON` to its executable in the same shell:

```powershell
$env:CARGO_TARGET_DIR = "C:\Temp\offspace-release-target"
$env:OFFSPACE_PYTHON = "C:\Path\To\Python312\python.exe"
npm run build
npm run build:backend
npm run tauri -- build --bundles msi
```

For an already-built release, the validated packaging command was:

```powershell
$env:CARGO_TARGET_DIR = "C:\Temp\offspace-release-target"
npm run tauri -- bundle --bundles msi --no-sign --verbose
```

This produced the MSI listed above. The `--no-sign` option was used for this validation only; the artifact is not suitable for distribution without a trusted signing process. Tauri's MSI bundler downloaded its pinned WiX version and verified its checksum. The NSIS target remains configured by default; MSI was selected with a CLI override. A separate direct-executable test previously verified backend startup/readiness, clean shutdown, and the missing-sidecar error message. Those results do not establish shutdown of the installed MSI app.

## Configuration

For source development, copy `.env.example` to `.env` in the project root. Supported settings include:

- `OFFSPACE_SECRET_KEY`
- `OFFSPACE_DEFAULT_PROVIDER`
- `OPENAI_API_KEY` or `OFFSPACE_OPENAI_API_KEY`
- `OFFSPACE_LOCAL_AI_URL`
- `OFFSPACE_LOCAL_AI_MODEL`

Never commit `.env` or print API key values. The packaged backend runs from `%LOCALAPPDATA%\Offspace`; it accepts environment variables and reads a local `.env` from its working directory. There is no verified installed-app settings flow for managing provider credentials.

For OpenAI, set one supported key variable in the environment available to OFFSPACE. For Ollama, install and start Ollama, then select the local provider and an installed model in OFFSPACE. The current default model is `llama3.2`; installing a model may require a large download, so obtain user approval before running `ollama pull llama3.2`.

The intended backend app-data directory is `%LOCALAPPDATA%\Offspace`, and the Tauri manager starts the packaged sidecar with that working directory. Tauri sets `OFFSPACE_DATABASE_URL` to `%LOCALAPPDATA%\Offspace\offspace.db`, and `backend/database/session.py` now prefers that value. Legacy `DATABASE_URL` remains a compatibility fallback. No database migration or existing-database modification is performed. Back up before any future migration. Backend diagnostics are written to `%LOCALAPPDATA%\Offspace\backend.log`.

## Voice compatibility

Python 3.12.10 with the project's SpeechRecognition and PyAudio dependencies was verified for imports and microphone enumeration. The regression suite also passed under Python 3.14.6, but that alone does not establish full Python 3.14 release compatibility. A prior recording attempt returned no transcript; real speech recognition, acoustic wake phrase activation, and audible desktop TTS have not been verified.

## Installation verification

The MSI installed successfully on Windows 11 to `C:\Program Files\Offspace Desktop`; installed executable and sidecar hashes match the release files, and the installed frontend/backend health check passed. The app launched despite the installer launch checkbox being unchecked; the cause was not established. The installation was not isolated from the user's profile. Database size and modification time were unchanged, but the database was not read and the backend log changed during startup/health requests. The user could not close the native app window, so installed backend shutdown and MSI uninstallation remain **blocked**; no process-kill workaround or uninstall was attempted.

The Python suite passed 39 tests (one existing `PytestReturnNotNoneWarning`), `npm run build` passed, `cargo check` passed, and `cargo test` passed 2 lifecycle tests. Automated tests cover provider error handling, memory/settings persistence in a temporary test database, automation path boundaries and delete confirmation, and the Tauri localhost CORS origin. No live OpenAI request was made because no credential was configured; Ollama had no available model and none was downloaded. No chat was sent from the installed UI. Production-origin CORS behavior was not tested; configured defaults include localhost development origins and allow all methods/headers. The MSI is unsigned, and its WiX warnings have not been resolved.

### Phase 1 source lifecycle update

- The packaged backend now receives `OFFSPACE_DATABASE_URL` pointing to `%LOCALAPPDATA%\Offspace\offspace.db`.
- The SQLAlchemy session prefers `OFFSPACE_DATABASE_URL`, then legacy `DATABASE_URL`, then the source fallback.
- Tauri validates the health response's status, database connection field, and version instead of accepting only a generic status substring.
- Tauri sends `OFFSPACE_SHUTDOWN` over the sidecar stdin and waits up to five seconds for FastAPI lifespan shutdown.
- If the sidecar does not exit, Tauri force-terminates only the process tree that it owns and confirms the direct child exit where possible.
- Startup timeout, missing sidecar, early exit, and owned-process-tree cleanup are covered by isolated tests.

A fresh MSI was built at `C:\Temp\offspace-phase1-msi-20261127-1304\cargo-target\release\bundle\msi\Offspace Desktop_0.1.0_x64_en-US.msi` (32,157,696 bytes, unsigned). It has not been installed. The prior MSI and existing installation were preserved, so the Phase 1 lifecycle fixes remain unverified in the installed environment.

**Release decision: NOT READY for distribution.** Complete a safe installed shutdown/uninstall test, repeat testing with an isolated user profile, verify installed chat/data persistence and production CORS, and sign/review the installer before release.
