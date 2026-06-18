
ALTER TABLE bots
    ADD COLUMN IF NOT EXISTS uipath_test_set_id TEXT;

CREATE TABLE IF NOT EXISTS test_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    synthetic_patient_id UUID REFERENCES synthetic_patients(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'queued',   
    uipath_execution_id TEXT,
    uipath_test_set_id TEXT,
    detail TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_test_runs_started_at ON test_runs USING BRIN (started_at);
CREATE INDEX IF NOT EXISTS idx_test_runs_bot_id ON test_runs (bot_id);