CREATE KEYSPACE IF NOT EXISTS finance 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE IF NOT EXISTS finance.raw_financial_data (
    symbol text,
    timestamp timestamp,
    open double,
    high double,
    low double,
    close double,
    volume bigint,
    PRIMARY KEY ((symbol), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE TABLE IF NOT EXISTS finance.processed_financial_data (
    symbol text,
    window_start timestamp,
    window_end timestamp,
    avg_price double,
    total_volume bigint,
    max_price double,
    min_price double,
    PRIMARY KEY ((symbol), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC);