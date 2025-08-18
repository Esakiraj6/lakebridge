-- Expected Databricks output for Oracle variable declarations

-- NUMBER variable -> BIGINT
DECLARE VARIABLE p_date_start BIGINT;

-- VARCHAR2 variable -> STRING
DECLARE VARIABLE v_name STRING;

-- DATE variable -> DATE  
DECLARE VARIABLE v_birth_date DATE;

-- TIMESTAMP variable -> TIMESTAMP
DECLARE VARIABLE v_created_at TIMESTAMP;

-- CHAR variable -> STRING
DECLARE VARIABLE v_status STRING;
