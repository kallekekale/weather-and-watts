CREATE TABLE IF NOT EXISTS prices (
    time   TIMESTAMPTZ,
    price  FLOAT,
    PRIMARY KEY (time)
);
