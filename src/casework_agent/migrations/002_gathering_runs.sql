CREATE TABLE IF NOT EXISTS gathering_runs(
    case_id TEXT PRIMARY KEY REFERENCES cases(id),
    run_id TEXT NOT NULL,
    owner_id TEXT,
    worker_generation INTEGER,
    CHECK((owner_id IS NULL AND worker_generation IS NULL) OR (owner_id IS NOT NULL AND worker_generation IS NOT NULL))
);
