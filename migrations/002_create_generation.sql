CREATE TABLE IF NOT EXISTS generation (
    dataset_id  INTEGER,
    start_time  TIMESTAMPTZ,
    end_time    TIMESTAMPTZ,
    value       FLOAT,
    PRIMARY KEY (dataset_id, start_time)
);
