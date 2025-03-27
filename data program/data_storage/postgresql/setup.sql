CREATE TABLE IF NOT EXISTS raw_financial_data (
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open DECIMAL(18,4),
    high DECIMAL(18,4),
    low DECIMAL(18,4),
    close DECIMAL(18,4),
    volume BIGINT,
    PRIMARY KEY (symbol, timestamp)
);

CREATE TABLE IF NOT EXISTS processed_financial_data (
    symbol VARCHAR(10),
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    avg_price DECIMAL(18,4),
    total_volume BIGINT,
    max_price DECIMAL(18,4),
    min_price DECIMAL(18,4),
    PRIMARY KEY (symbol, window_start)
);