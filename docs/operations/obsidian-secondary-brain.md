# Obsidian Secondary Brain

## Purpose and boundary

This is the private personal knowledge layer for VEGO-AI work. Obsidian is the
human-facing Markdown vault; it is not an AI service, a cloud archive, or a
GitHub publishing target. The raw archive and its SQLite indexes stay in a
locally encrypted folder outside the repository. The vault produces safe
metadata notes, hash receipts, and source-state dashboards only.

The implementation is free and local. It has no telemetry, cloud replication,
GitHub upload, paid model, payment, bank access, purchase, or automatic
external synchronization.

## Supported sources

| Source | State before consent/export | Permitted behavior |
| --- | --- | --- |
| Gmail | `needs_authorization` | Official OAuth, read-only import only. No send, archive, delete, label, forward, or share action. |
| Google Drive | `needs_authorization` | Official OAuth, read-only import only. No sharing, moving, deleting, or permission change. |
| ChatGPT, Claude, Gemini | `needs_authorization` | Import an official export or other user-authorized local export. Browser session scraping is prohibited. |
| Codex | `import_ready` | Import a user-authorized export or local session artifact; record provenance. |
| Local folders | `import_ready` | Scan only approved roots. Credential material, browser profiles, executables, keys, and system locations are rejected. |
| Bills | `import_ready` | Extract reminder candidates locally and mark them for human review. Paying, banking, transfers, and provider contact are unsupported. |

Each imported record has a stable ID, a SHA-256 receipt, source class,
classification, archival time, and deletion receipt. Imports are idempotent by
content hash.

## Obsidian layout

The initializer creates these folders under `Obsidian Notes`:

- `Inbox` — user-reviewed capture landing zone.
- `Sources` — content-free source metadata notes.
- `Bills` — human-reviewed reminder candidates only.
- `Activity` — hash-linked interaction provenance; no prompt or response body.
- `Receipts` — deletion and integrity receipts.

`Secondary Brain Dashboard.md` lists connector state and the privacy boundary.
It intentionally includes neither raw body text nor source file paths.

## Initialize locally

Run the setup script without switches first to review the requested location.
It does not create a vault in that mode. After confirming a location on a
Windows device with EFS, initialize with:

```powershell
.\scripts\setup-obsidian-secondary-brain.ps1 -Initialize
```

The script encrypts the vault folder with Windows EFS and verifies an explicit
encrypted file status before the application writes vault data. Failure to
verify stops the process before personal content is imported. Device encryption
is not treated as a substitute unless it can be independently verified by the
operator.

The optional `-RegisterLocalReminderTask` parameter installs a daily local
dashboard/reminder refresh. It does not connect to external systems or alter
any source. Review the scheduled task before enabling it.

## Release rule

This repository may contain only the implementation, tests, source hashes of
approved project-safe records, and sanitized VEGO-AI documentation. Do not add
an Obsidian vault, raw mail, attachments, bills, media, transcripts, Drive IDs,
browser URLs, credentials, private paths, or OAuth tokens to Git.
