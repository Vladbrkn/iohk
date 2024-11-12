WITH portfolio_metrics AS (
    SELECT
        COUNT(DISTINCT loan_id) AS total_loans,
        -- SUM(collection_rate),
        SUM(write_off_amount) / SUM(principal_amount) *100,
        SUM(actual_interest) / SUM(principal_amount) * 100 AS gross_yield,
        AVG(avg_days_in_arrears)
    FROM {{ ref('silver_model') }}
)
SELECT *
FROM portfolio_metrics
