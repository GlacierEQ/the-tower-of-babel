CREATE TABLE IF NOT EXISTS tower_mission (
  mission_id TEXT PRIMARY KEY,
  objective TEXT NOT NULL,
  plan_sha256 TEXT NOT NULL CHECK (length(plan_sha256) = 64),
  authority_status TEXT NOT NULL CHECK (authority_status IN ('SUCCEEDED', 'BLOCKED')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tower_event (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  mission_id TEXT NOT NULL REFERENCES tower_mission(mission_id),
  stage TEXT NOT NULL,
  status TEXT NOT NULL,
  evidence_sha256 TEXT NOT NULL CHECK (length(evidence_sha256) = 64)
);
