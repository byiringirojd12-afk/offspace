# OFFSPACE Security Posture

This is a current-state summary, not a complete security certification. The installed MSI workflow and production CORS policy have not passed release acceptance.

## Implemented and exercised

- The active API has registration/login/profile routes, hashes passwords, and authenticates protected routes with JWTs.
- API keys are read from environment/settings; no key values are included in this document or logs intentionally.
- Active memory and settings routes are user-scoped through authenticated request dependencies.
- The legacy `core.automation` create/delete paths check workspace containment, and its shell path uses an executable allowlist. Tests cover path escape rejection and confirmation before deleting a test file.
- Provider tests cover sanitized OpenAI error messages. These are unit tests, not live provider validation.

## Verified gaps

- The active Tauri chat route does not currently invoke automation, agents, or approval modules. Do not treat legacy tool code as a supported secure execution path.
- `core.security.PermissionManager.request_permission()` sets a permission to allowed immediately. This is not a user approval interface and violates the required approval-based autonomy if used as-is.
- `backend/tools/system_tool.py` and the Windows branch of `backend/automation/apps.py` use `shell=True`. The file tool lacks workspace containment and approval checks. They were not found in the packaged API call path; keep them isolated until dependency review and replacement.
- Approval checkpoints and audit logs are in-memory scaffolding and are not connected to active API execution or durable audit storage.
- The default CORS list contains development localhost origins; middleware enables credentials and allows all methods/headers. Tauri has `csp: null`. Only the Tauri localhost CORS test is automated; no production allow/deny policy is validated.
- The settings code creates a random JWT secret if no stable secret is configured. Authentication continuity across restarts depends on a stable secret being present. Verify presence without logging its value before release.
- `backend/database/session.py` prefers `OFFSPACE_DATABASE_URL`, then uses legacy `DATABASE_URL`, then the source-development fallback. Tauri sets `OFFSPACE_DATABASE_URL` to `%LOCALAPPDATA%\Offspace\offspace.db`; confirm and back up the active database before any future path change or migration.
- No complete security audit, installed automation test, or signed installer validation has been performed.

## Required controls before automation is connected

1. Require explicit, action-specific user approval for every sensitive operation; never grant permission as a side effect of a request.
2. Validate typed tool arguments and canonicalize paths; enforce a user-selected permitted root for read, write, search, and delete.
3. Do not execute user-controlled shell strings. Replace legacy shell use with narrowly defined operations and fixed executable/argument mappings.
4. Persist privacy-conscious audit events for approvals and sensitive actions, excluding credentials and private content.
5. Keep provider credentials outside source and never print them. Keep local-provider requests local unless the user explicitly selects cloud.
6. Define environment-specific CORS/CSP policy and test both allowed and denied origins before release.
7. Keep database migrations and key changes behind a verified backup and an explicit data-preservation test.

See [architecture.md](./architecture.md) for the active and target data flows.
