# OFFSPACE Windows MVP Release Validation

## Summary

Validation continued on Windows 11 (build 26300); no commits or pushes were created. A Tauri MSI was generated and installed per-machine at `C:\Program Files\Offspace Desktop`. Its desktop executable and backend sidecar match the release binaries, and the installed UI displayed a connected backend; the health endpoint returned online with its database connected. The test was not isolated from the user's app-data environment. The database file's size and modification time did not change, but its contents were not read; `backend.log` grew during startup and health checks. The user could not close the native app window, so installed-app shutdown and uninstallation remain unverified. OFFSPACE is **not ready for release**.

## Backend integration and packaging

- **PASS — Phase 1 lifecycle fixes implemented:** the backend now resolves `OFFSPACE_DATABASE_URL` before legacy `DATABASE_URL`, and Tauri now requests a private stdin shutdown command, waits for FastAPI lifespan shutdown, and falls back only to taskkill of the OFFSPACE-owned process tree. OFFSPACE-specific readiness now requires status `online`, database `connected`, and a nonempty version field. Graceful and forced cleanup are bounded and logged.
- **PASS — Isolated lifecycle validation:** 13 backend lifecycle/health tests passed. Rust lifecycle tests passed 10/10, including graceful shutdown, timeout cleanup, missing sidecar handling, and owned-process-tree fallback.

- **PASS — Backend sidecar build:** `scripts/build_backend.mjs` produced `src-tauri\binaries\offspace-backend.exe` with Python 3.12.10 and PyInstaller 6.15.0. The backend runtime requirements now declare `PyJWT` and `bcrypt`, which were missing from the first sidecar and prevented authentication from loading.
- **PASS — Sidecar API smoke test:** using a newly created temporary SQLite database, the packaged backend returned a healthy response and completed registration, login, authenticated memory save, and memory search. The smoke test did not access the user's `%LOCALAPPDATA%\Offspace\offspace.db`.
- **PASS — Readiness checks:** Rust tests verify that readiness requires the OFFSPACE health response and rejects an unrelated HTTP listener. `cargo test` passed both tests.
- **PASS — Database URL contract corrected:** `backend/database/session.py` now prefers `OFFSPACE_DATABASE_URL`, retains `DATABASE_URL` as the compatibility fallback, and retains the relative fallback for source development. Tauri sets it to `%LOCALAPPDATA%\Offspace\offspace.db` for the packaged backend. This is URL selection only; no existing database was migrated or modified.
- **PASS — Tauri-managed sidecar startup and frontend connection:** launched the freshly built release executable at `C:\Temp\offspace-release-target\release\offspace-desktop.exe`. Its packaged sidecar started from the same release directory; the UI displayed “Backend connected. System ready.” and `GET /api/v1/health` returned `{"status":"online","version":"1.0.0"}`.
- **PASS — Direct-executable backend shutdown:** after closing the directly launched release executable (not the MSI-installed app), both the desktop and sidecar processes exited, port 8000 was free, and the health endpoint was unavailable.
- **PASS — Startup failure feedback:** launched a temporary copy of the desktop executable without its sidecar. The UI showed “OFFSPACE backend did not become ready” with the backend log location; `backend.log` recorded that the packaged resource was missing. The temporary test copy was removed.
- **PASS — Duplicate-listener check:** the one-file PyInstaller sidecar ran its bootloader/worker process pair, with one worker listening on port 8000. No second backend listener was observed.
- **NOT TESTED — Desktop memory persistence across restart:** authenticated memory save/search passed in the isolated sidecar smoke test and Python workflow tests. I did not write test records to the existing app database, so persistence through a Tauri app restart remains unverified.

## Windows executable and installer

- **PASS — Frontend production build:** `npm run build`.
- **PASS — Rust compile check:** `cargo check --manifest-path src-tauri\Cargo.toml`.
- **PASS — Rust lifecycle tests:** `cargo test --manifest-path src-tauri\Cargo.toml` — 2 passed.
- **PASS — Build-output root cause and recovery:** `CARGO_TARGET_DIR` was unset and no Cargo target-dir config was present. `src-tauri\target` is a Microsoft Cloud Files reparse point inside OneDrive; its release build directories carry the read-only attribute. The current user has ACL Full Control, disk space was ample, and no Cargo/Rust build was active at diagnosis. The `autocfg` build script explicitly rejects a read-only `OUT_DIR`, causing `output path is not a writable directory`. Preserving the original target, the build was redirected per-command to `C:\Temp\offspace-release-target`.
- **PASS — Windows release executable:** Tauri release compilation completed in 19m 11s. Executable: `C:\Temp\offspace-release-target\release\offspace-desktop.exe` (8,436,736 bytes). The packaged sidecar is `C:\Temp\offspace-release-target\release\offspace-backend.exe` (29,793,088 bytes).
- **PASS — Packaging toolchain:** Tauri CLI 2.11.4 supports `msi` and `nsis`. NSIS 3.13 is installed, but Tauri requires its pinned NSIS 3.11; the earlier GitHub download failed with `os error 10054`. NSIS 3.13 was not substituted and the failed download was not retried. Tauri obtained and checksum-validated its pinned WiX 3.14.1 toolset (`candle`/`light` 3.14.1.8722), enabling the MSI route.
- **PASS — MSI generation and payload:** `C:\Temp\offspace-release-target\release\bundle\msi\Offspace Desktop_0.1.0_x64_en-US.msi` exists and is 32,157,696 bytes. The generated WiX source lists `offspace-desktop.exe`, the configured `offspace-backend.exe` resource, and the product icon. Both installed executables are present under `C:\Program Files\Offspace Desktop`; their SHA-256 hashes match the release binaries. The existing Tauri target remains NSIS; MSI was selected with the CLI override. The existing `src-tauri\icons\icon.ico` was configured because the MSI bundler requires an icon.
- **PASS — MSI installation and initial launch:** the per-machine MSI installation completed under `C:\Program Files\Offspace Desktop`. The installed frontend displayed “Backend connected. System ready.” A direct request to `http://127.0.0.1:8000/api/v1/health` returned status `online`, database `connected`, version `1.0.0`. The MSI's launch checkbox was unchecked, but the app and backend were subsequently observed running; the cause of that launch was not established. This was not an isolated test-profile install and no chat request was sent.
- **BLOCKED — Installed shutdown and uninstall:** the installed window remains open. The user reported being unable to close it. No process termination workaround was used and no uninstall was attempted; the MSI remains installed. The database remained 40,960 bytes with its pre-test modification time, but the database was not read, so this metadata alone does not prove that no database writes occurred. `backend.log` grew from 1,176 to 3,801 bytes during startup and health requests.
- **WARN — MSI release quality:** the MSI was built with `--no-sign` and is not digitally signed. WiX emitted ICE03, ICE40, ICE57, and ICE61 warnings. Tauri also warned that the existing executable lacked `__TAURI_BUNDLE_TYPE`; updater behavior was not tested.

## AI providers

- **BLOCKED — OpenAI live test:** neither supported key variable nor an OpenAI key in the local `.env` was configured. No live request was made and no credential was printed. Mocked provider tests cover configuration aliases and sanitized error handling; they are not live validation.
- **BLOCKED — Ollama live response:** the local server was reachable, but reported zero available models. No model was downloaded and no real completion was generated. To retry, start Ollama and install the configured model only with the user's approval, for example `ollama pull llama3.2`.

## Integration verification

- **PASS — Automated memory and settings persistence:** the Python suite saves a setting and memory item to its temporary test database, recreates the test client, and reads them back. This does not verify persistence in the installed app's existing database.
- **PASS — Automated automation and security cases:** tests cover file creation/search in a temporary directory, rejection of paths outside that directory, and confirmation before deleting a file. Provider tests verify that selected error messages do not expose credentials or response bodies. This is regression coverage, not a complete security audit.
- **PASS — Tauri CORS origin test:** the automated suite verifies that `http://tauri.localhost` receives the expected CORS response for the health route.
- **NOT TESTED — Production CORS policy:** the settings use the same origin list across environments; the defaults include localhost development origins, and CORS methods and headers are `*`. No production-origin allow/deny test was run.
- **NOT TESTED — Installed chat or live provider flow:** no chat was sent from the installed UI. OpenAI has no configured credential, and Ollama has no available model.

## Voice and hardware

- **PASS — Python 3.12 dependency/import checks:** prior validation confirmed Python 3.12.10 with SpeechRecognition, PyAudio and `aifc`; microphone device enumeration and a `pyttsx3` invocation also completed.
- **FAIL — Prior microphone recognition attempt:** a previously approved capture returned an empty transcript. No successful recognition is claimed, and no new microphone recording or external speech-recognition request was made.
- **NOT TESTED — Wake phrase and desktop voice workflow:** no acoustic wake phrase or complete spoken desktop interaction was verified. TTS engine invocation alone does not establish audible output.
- Python 3.12.10 is the voice-stack version verified in this environment; the project's formal minimum supported Python version has not been established. Python 3.14 compatibility remains unverified.

## Regression results

- **PASS — Python suite:** 39 passed under the project virtual environment (Python 3.14.6). Pytest reports one existing `PytestReturnNotNoneWarning` from `backend/voice/microphone_test.py`; that diagnostic enumerates devices and is not a recording/recognition test.
- **PASS — Frontend production build:** `npm run build`.
- **PASS — Rust checks:** `cargo check` passed; `cargo test` passed 2 lifecycle readiness tests.
- **PASS — Current baseline rerun:** the isolated Python suites passed 40 tests. The frontend production build passed. `cargo check` passed and Rust lifecycle tests passed 10/10 using the separate Cargo target. A live health request remains separately unverified for this source revision. A fresh MSI was subsequently built in a separate output directory; it has not been installed and the prior MSI was not overwritten.
- **DATA NOTE — Legacy test memory path:** one Assistant test writes to `.offspace/memory.db`; after the suite it measured 28,672 bytes, and no pre-test metadata was captured. The database contents were not read. With the user's approval, the post-test file was copied to `C:\Temp\offspace-baseline-backup-20261127-1116\memory.db`; the original was not altered by that copy. Isolate this test's memory path before rerunning it.
- **PASS — Tauri release compilation and MSI packaging:** the executable was built with `CARGO_TARGET_DIR=C:\Temp\offspace-release-target`; MSI bundling succeeded with the checksum-pinned WiX toolset. NSIS packaging was not attempted because the installed 3.13 compiler does not match Tauri's pinned 3.11 dependency.
- **PASS — Packaged backend smoke:** health, registration/authentication, memory save/search, and login passed against a disposable database.
- **PASS — Mocked provider, workflow, voice, and automation tests:** covered by the Python suite; these do not substitute for external provider, microphone, or physical automation validation.

## Linux

- **BLOCKED — Linux tests and desktop build:** no Linux environment or CI runner was available for this validation; Linux compatibility is not claimed.

## Remaining blockers and release decision

1. Close OFFSPACE safely, verify the installed backend stops and port 8000 closes, then uninstall the MSI only after the app is no longer running. Verify installed-data behavior without deleting the user's database.
2. Repeat installation and lifecycle tests in an isolated Windows test profile/location; verify chat and installed-app settings/memory persistence.
3. Sign the MSI and executables for distribution and resolve/review the WiX ICE and `__TAURI_BUNDLE_TYPE` warnings.
4. Review and test an environment-specific production CORS policy; current automated coverage only checks the Tauri localhost origin.
5. Configure an OpenAI key for a real provider request and make an Ollama model available for real local inference, with user approval before any model download.
6. Repeat microphone capture and recognition with authorization; verify wake phrase and audible desktop TTS.
7. Run Linux validation.

**Release decision: NOT READY for Windows 11 distribution.** A real MSI installed and launched the frontend and backend, but the installed app has not been shut down or uninstalled, testing was not isolated, and installed chat/data persistence remain unverified. The MSI is unsigned; production CORS, live AI providers, hardware voice, and Linux validation also remain incomplete.

## Changes and working-tree note

The local inspection reran the frontend, Python, and Rust baselines and rechecked the installed health endpoint. It identified and authorized fixes for the database variable mismatch, shallow readiness validation, force-only shutdown, and missing child-process cleanup logging. No installed app was closed or terminated, no MSI was installed or uninstalled, and no existing database was migrated or modified. Isolated tests used temporary working directories and databases. Existing unrelated working-tree changes and build artifacts were preserved. No commit or push was created.
