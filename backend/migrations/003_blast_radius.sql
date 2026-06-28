-- 003_blast_radius.sql — Day 4 (Feature 12, Cascade Blast Radius Mapping)
-- Per-bot 24h throughput estimate. Drives the "patients at risk" counter.

ALTER TABLE bots
    ADD COLUMN IF NOT EXISTS daily_patient_volume INTEGER NOT NULL DEFAULT 0;