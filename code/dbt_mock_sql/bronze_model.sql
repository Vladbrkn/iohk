WITH loans_raw AS (
    SELECT 
        loan_id,
        borrower_id,
        issue_date,
        maturity_date,
        closing_date,
        currency,
        principal_amount,
        interest_rate,
        write_off_date,
        write_off_amount,
        default_date,
        default_amount,
        product_name,
        penalties,
        fees,
        total_outstanding,
        as_of_datetime
    FROM {{ ref('loans_raw') }} 
),
payments_raw AS (
    SELECT 
        payment_id,
        payment_date,
        loan_id,
        currency,
        amount,
        type
    FROM {{ ref('payments_raw') }} 
),
borrowers_raw AS (
    SELECT 
        borrower_id,
        gender,
        country,
        geo_classification,
        date_of_birth,
        as_of_datetime
    FROM {{ ref('borrowers_raw') }}  
)
