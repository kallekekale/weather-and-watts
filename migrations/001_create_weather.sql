CREATE TABLE IF NOT EXISTS weather (
    station_id      INTEGER,
    time            TIMESTAMPTZ,
    parameter_name  VARCHAR(50),
    parameter_value FLOAT,
    PRIMARY KEY (station_id, time, parameter_name)
);
