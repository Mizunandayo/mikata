-- 001_init.sql  — MIKATA core schema (PostgreSQL 13+, plain tables + BRIN, Decision 3)

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);

-- Core bot registry
CREATE TABLE IF NOT EXISTS bots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    patient_impact_level INTEGER NOT NULL CHECK (patient_impact_level IN (1, 2, 3)),
    patient_impact_score NUMERIC(5,2) NOT NULL,
    pis_reasoning TEXT,                       -- Explainability trace (Feature 16)
    automation_debt_score NUMERIC(5,2) DEFAULT 0,
    registered_at TIMESTAMPTZ DEFAULT NOW(),
    last_tested_at TIMESTAMPTZ,
    last_test_result TEXT,                    -- 'pass' | 'fail' | NULL
    healing_agent_enabled BOOLEAN DEFAULT true
);

-- Dependency graph edges (mirrors Neo4j for fast SQL joins / Risk 3 fallback)
CREATE TABLE IF NOT EXISTS bot_dependencies (
    upstream_bot_id UUID REFERENCES bots(id) ON DELETE CASCADE,
    downstream_bot_id UUID REFERENCES bots(id) ON DELETE CASCADE,
    data_field TEXT NOT NULL,
    criticality TEXT NOT NULL CHECK (criticality IN ('hard', 'soft')),
    PRIMARY KEY (upstream_bot_id, downstream_bot_id, data_field)
);

-- Time-series execution events (plain table + BRIN index, Decision 3)
CREATE TABLE IF NOT EXISTS execution_events (
    id UUID DEFAULT gen_random_uuid(),
    bot_id UUID REFERENCES bots(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,                 -- 'test_pass','test_fail','compliance_drift','production_run'
    patient_volume INTEGER,
    drift_score NUMERIC(5,4),
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    payload JSONB
);
CREATE INDEX IF NOT EXISTS idx_execution_events_recorded_at
    ON execution_events USING BRIN (recorded_at);

-- Golden Hour Protocol cases
CREATE TABLE IF NOT EXISTS golden_hour_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID REFERENCES bots(id) ON DELETE CASCADE,
    activated_at TIMESTAMPTZ DEFAULT NOW(),
    protocol_state TEXT NOT NULL DEFAULT 'healing_attempt',
    healing_result TEXT,
    ops_acknowledged_at TIMESTAMPTZ,
    clinical_notified_at TIMESTAMPTZ,
    executive_notified_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    protocol_breached BOOLEAN DEFAULT false,
    maestro_case_id TEXT,
    blast_radius_json JSONB
);

-- Bot Witness forensic records
CREATE TABLE IF NOT EXISTS bot_witness_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id UUID REFERENCES bots(id) ON DELETE CASCADE,
    execution_id TEXT NOT NULL,
    recorded_at TIMESTAMPTZ DEFAULT NOW(),
    execution_log JSONB NOT NULL,
    sha256_signature TEXT NOT NULL,
    signature_verified BOOLEAN DEFAULT true,
    hipaa_audit_ready BOOLEAN DEFAULT false
);

-- Automation Debt Score history (time-series, plain table + BRIN index)
CREATE TABLE IF NOT EXISTS debt_score_history (
    bot_id UUID REFERENCES bots(id) ON DELETE CASCADE,
    score NUMERIC(5,2) NOT NULL,
    computed_at TIMESTAMPTZ DEFAULT NOW(),
    failure_frequency_component NUMERIC(5,2),
    mttr_component NUMERIC(5,2),
    blast_radius_component NUMERIC(5,2),
    interface_volatility_component NUMERIC(5,2),
    compliance_drift_component NUMERIC(5,2)
);
CREATE INDEX IF NOT EXISTS idx_debt_score_history_computed_at
    ON debt_score_history USING BRIN (computed_at);

-- Regulatory change events
CREATE TABLE IF NOT EXISTS regulatory_changes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    change_summary TEXT NOT NULL,
    detected_at TIMESTAMPTZ DEFAULT NOW(),
    affected_bots JSONB,
    test_cases_staged INTEGER DEFAULT 0,
    preflight_scheduled BOOLEAN DEFAULT false
);

-- Compliance baseline profiles
CREATE TABLE IF NOT EXISTS compliance_baselines (
    bot_id UUID REFERENCES bots(id) ON DELETE CASCADE PRIMARY KEY,
    schema_version TEXT NOT NULL,
    required_fields JSONB NOT NULL,
    value_constraints JSONB,
    format_specifications JSONB,
    -- Feature 7 (Authorization Drift) rides on this same profile per blueprint
    scope_of_authority JSONB,
    last_updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT
);

-- Synthetic patient cohort (Synthea output, parsed FHIR R4)
CREATE TABLE IF NOT EXISTS synthetic_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    synthea_id TEXT NOT NULL,
    profile TEXT,                             -- 'pediatric','geriatric','oncology', etc.
    fhir_bundle JSONB NOT NULL,
    summary JSONB NOT NULL,                   -- flattened demographics + dx + insurance
    generated_at TIMESTAMPTZ DEFAULT NOW()
);
