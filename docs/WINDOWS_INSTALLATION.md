# Windows Build and Installation

## Current release status

The current Tauri executable and packaged backend were built and launched successfully:

- Executable: `C:\Temp\offspace-release-target\release\offspace-desktop.exe`
- Backend resource: `C:\Temp\offspace-release-target\release\offspace-backend.exe`

The UI reported the backend connected, the health endpoint returned online, and closing the application stopped the sidecar. A copied executable without the sidecar displayed the backend-not-ready message and log location.

There is **no installer**. Tauri CLI 2.11.4 attempted to download its pinned `nsis-3.11.zip` from GitHub after release compilation, but the connection was forcibly closed (`os error 10054`). The machine has NSIS 3.13 at `C:\Program Files (x86)\NSIS\makensis.exe`; this does not replace Tauri's pinned dependency. No repeated download or unsupported compiler substitution was attempted.

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
6. NSIS for the configured installer target. The installed NSIS 3.13 has not yet been verified by a completed Tauri bundle.
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
$env:NSISDIR = "C:\Program Files (x86)\NSIS"
$env:PATH = "$env:NSISDIR;$env:PATH"
npm run build
npm run build:backend
npm run tauri -- build --bundles nsis
```

Tauri creates the desktop executable and stages `offspace-backend.exe` beside it in the target release directory. The sidecar was launched by the actual Tauri executable and passed health/readiness and shutdown checks. An isolated missing-sidecar launch also verified the user-facing failure message. The installed workflow and desktop memory persistence across an app restart have not been tested.

## Configuration

For source development, copy `.env.example` to `.env` in the project root. Supported settings include:

- `OFFSPACE_SECRET_KEY`
- `OFFSPACE_DEFAULT_PROVIDER`
- `OPENAI_API_KEY` or `OFFSPACE_OPENAI_API_KEY`
- `OFFSPACE_LOCAL_AI_URL`
- `OFFSPACE_LOCAL_AI_MODEL`

Never commit `.env` or print API key values. The packaged backend runs from `%LOCALAPPDATA%\Offspace`; it accepts environment variables and reads a local `.env` from its working directory. There is no verified installed-app settings flow for managing provider credentials.

For OpenAI, set one supported key variable in the environment available to OFFSPACE. For Ollama, install and start Ollama, then select the local provider and an installed model in OFFSPACE. The current default model is `llama3.2`; installing a model may require a large download, so obtain user approval before running `ollama pull llama3.2`.

The backend database is stored under `%LOCALAPPDATA%\Offspace\offspace.db`. Backend diagnostic output is written to `%LOCALAPPDATA%\Offspace\backend.log`. Do not remove these files when upgrading if user data must be retained.

## Voice compatibility

Python 3.12.10 with the project's SpeechRecognition and PyAudio dependencies was verified for imports and microphone enumeration. A prior recording attempt returned no transcript; real speech recognition, acoustic wake phrase activation, and audible desktop TTS have not been verified. Python 3.14 compatibility is not established.

## Installation verification

No installer artifact has been generated. The expected NSIS output directory `C:\Temp\offspace-release-target\release\bundle\nsis` was not created. Therefore installer installation and installed-data persistence are **not tested**. Do not distribute the current build as an installer.
