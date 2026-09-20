# Database

Core entities:
- `users`: authenticated accounts and roles.
- `planets`: canonical target records and source payloads.
- `observations`: source/type/status metadata tied to targets.
- `analysis_runs`: immutable analysis result snapshots and ownership.
- `model_runs`: model/version/metrics used by an analysis.
- `saved_targets`: per-user bookmarks.
- `activity_logs`: auditable user actions.
- `alerts`: tracked target notifications.
- `comments`: target annotations.
- `workspaces`: future team/lab ownership boundary.
- `active_learning_queue`: uncertain candidate review queue.

Production should set `DATABASE_URL` to PostgreSQL. Local development automatically uses SQLite.
