WITH enriched_data AS (
    SELECT
        l.loan_id,
        l.borrower_id,
        l.issue_date,
        l.maturity_date,
        l.closing_date,
        l.currency,
        l.principal_amount,
        l.interest_rate,
        l.write_off_date,
        l.write_off_amount,
        l.default_date,
        l.default_amount,
        l.product_name,
        l.penalties,
        l.fees,
        l.total_outstanding,
        l.as_of_datetime,
        p.payment_id,
        p.payment_date,
        p.amount AS payment_amount,
        p.type AS payment_type,
        b.gender,
        b.country,
        b.geo_classification,
        b.date_of_birth,
        
        -- Calculating loan terms (in days and months)
        DATEDIFF(l.maturity_date, l.issue_date) AS expected_term_days,
        DATEDIFF(l.closing_date, l.issue_date) AS actual_term_days,
        
        -- Interest calculations
        l.principal_amount * l.interest_rate AS expected_interest,
        (l.principal_amount * l.interest_rate) / DATEDIFF(l.maturity_date, l.issue_date) AS expected_interest_daily,
        ((l.principal_amount * l.interest_rate) / DATEDIFF(l.maturity_date, l.issue_date)) * DATEDIFF(l.closing_date, l.issue_date) AS actual_interest,
        
        -- Write-off rate (calculated at the loan level)
        l.write_off_amount / l.principal_amount AS write_off_rate,
        
        -- Collection rate: ratio of payments received to total outstanding balances
        SUM(CASE WHEN p.payment_amount IS NOT NULL THEN p.payment_amount ELSE 0 END) / l.total_outstanding * 100 AS collection_rate,
        
        -- Days in arrears (calculated from closing and maturity dates)
        DATEDIFF(l.closing_date, l.maturity_date) AS days_in_arrears,
        
        -- Gross Yield (calculated at the loan level)
        ((l.principal_amount * l.interest_rate) / DATEDIFF(l.maturity_date, l.issue_date)) * DATEDIFF(l.closing_date, l.issue_date) / l.principal_amount * 100 AS gross_yield
        
    FROM {{ ref('bronze_model') }} AS l
    LEFT JOIN {{ ref('payments_raw') }} AS p ON l.loan_id = p.loan_id
    LEFT JOIN {{ ref('borrowers_raw') }} AS b ON l.borrower_id = b.borrower_id
    
    GROUP BY 
        l.loan_id, l.borrower_id, l.issue_date, l.maturity_date, l.closing_date, l.currency, 
        l.principal_amount, l.interest_rate, l.write_off_date, l.write_off_amount, 
        l.default_date, l.default_amount, l.product_name, l.penalties, l.fees, 
        l.total_outstanding, l.as_of_datetime, p.payment_id, p.payment_date, p.payment_amount, 
        p.payment_type, b.gender, b.country, b.geo_classification, b.date_of_birth
)
SELECT *
FROM enriched_data;
