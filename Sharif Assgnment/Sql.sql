
CREATE TABLE customers_staging (
    customer_id STRING,      -- كان INT، سنغيره إلى STRING
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");

LOAD DATA LOCAL INPATH '/tmp/customer_updated.csv' INTO TABLE customers_staging;




CREATE TABLE customers_internal (
    customer_id INT,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date DATE,
    start_date DATE,
    end_date DATE,
    is_current INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE;

INSERT OVERWRITE TABLE customers_internal
SELECT 
    customer_id,
    name,
    email,
    phone_number,
    address,
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(join_date, 'M/dd/yyyy'))) AS join_date,
    TO_DATE('2025-04-01') AS start_date,
    NULL AS end_date,
    1 AS is_current
FROM customers_staging;




CREATE EXTERNAL TABLE customers_external (
    customer_id INT,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date DATE,
    start_date DATE,
    end_date DATE,
    is_current INT
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/hive/warehouse/customers_external';

INSERT INTO customers_external
SELECT * FROM customers_internal;



DROP TABLE customers_internal;

DROP TABLE customers_external;

SHOW TABLES LIKE 'customers_staging';















-- جدول مؤقت لملف scd2
CREATE TABLE scd2_staging (
    CustomerID INT,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");

LOAD DATA LOCAL INPATH '/tmp/customer_scd2_mixed.csv' INTO TABLE scd2_staging;

-- جدول البُعد النهائي
CREATE TABLE customer_dim (
    customer_sk INT,
    customer_id INT,
    name STRING,
    email STRING,
    phone_number STRING,
    address STRING,
    join_date DATE,
    start_date DATE,
    end_date DATE,
    is_current STRING
)
STORED AS TEXTFILE;

-- تحميل البيانات الأولية مع مفتاح بديل
INSERT OVERWRITE TABLE customer_dim
SELECT
    ROW_NUMBER() OVER (ORDER BY CustomerID) AS customer_sk,
    CustomerID,
    Name,
    Email,
    Phone_Number,
    Address,
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(JOIN_Date, 'M/dd/yyyy'))) AS join_date,
    TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(Start_Date, 'M/dd/yyyy'))) AS start_date,
    NULL AS end_date,
    '1' AS is_current
FROM scd2_staging;





INSERT OVERWRITE TABLE customer_dim
SELECT
    ROW_NUMBER() OVER (ORDER BY sub.customer_id, sub.start_date) AS customer_sk,
    sub.customer_id,
    sub.name,
    sub.email,
    sub.phone_number,
    sub.address,
    sub.join_date,
    sub.start_date,
    sub.end_date,
    sub.is_current
FROM (
    -- 1) السجلات التي لم تتغير
    SELECT
        d.customer_id,
        d.name,
        d.email,
        d.phone_number,
        d.address,
        d.join_date,
        d.start_date,
        NULL AS end_date,
        '1' AS is_current
    FROM customer_dim d
    LEFT JOIN customers_staging u ON d.customer_id = CAST(u.customer_id AS INT)
    WHERE d.is_current = '1'
      AND u.customer_id IS NULL

    UNION ALL

    -- 2) إنهاء القديمة
    SELECT
        d.customer_id,
        d.name,
        d.email,
        d.phone_number,
        d.address,
        d.join_date,
        d.start_date,
        DATE_SUB(CURRENT_DATE, 1) AS end_date,
        '0' AS is_current
    FROM customer_dim d
    INNER JOIN customers_staging u ON d.customer_id = CAST(u.customer_id AS INT)
    WHERE d.is_current = '1'
      AND (d.name != u.name 
           OR d.email != u.email 
           OR d.phone_number != u.phone_number 
           OR d.address != u.address)

    UNION ALL

    -- 3) الجديدة والمُحدثة
    SELECT
        CAST(u.customer_id AS INT) AS customer_id,
        u.name,
        u.email,
        u.phone_number,
        u.address,
        TO_DATE(FROM_UNIXTIME(UNIX_TIMESTAMP(u.join_date, 'M/dd/yyyy'))) AS join_date,
        CURRENT_DATE AS start_date,
        NULL AS end_date,
        '1' AS is_current
    FROM customers_staging u
    LEFT JOIN customer_dim d ON CAST(u.customer_id AS INT) = d.customer_id AND d.is_current = '1'
    WHERE d.customer_id IS NULL
       OR (d.name != u.name 
           OR d.email != u.email 
           OR d.phone_number != u.phone_number 
           OR d.address != u.address)
) sub;





SELECT customer_sk, customer_id, name, email, phone_number, address, 
       join_date, start_date, end_date, is_current
FROM customer_dim
WHERE customer_id = 12402
ORDER BY start_date;
