DROP TABLE IF EXISTS crowdfounding_contracts;
CREATE TABLE crowdfounding_contracts (
    founder CHAR(64),
    pool_name CHAR(64),
    target BIGINT,
    startTime BIGINT,
    endTime BIGINT,
    create_tx_id CHAR(64),
    app_id BIGINT

);