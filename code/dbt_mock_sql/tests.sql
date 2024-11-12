-- below examples of tests that can be implemented in dbt

models:
  - name: bronze_model
    description: "Raw data ingested from source systems"
    columns:
      - name: loan_id
        description: "Unique identifier for each loan"
        tests:
          - not_null
          - unique
      - name: principal_amount
        description: "Amount of the loan"
        tests:
          - not_null
          - accepted_values:
              values: ['>= 0']

  - name: silver_model
    description: "Enriched data with calculated metrics"
    columns:
      - name: write_off_rate
        description: "Write-off rate for each loan"
        tests:
          - not_null
          - accepted_range:
              min: 0
              max: 100

  - name: gold_model
    description: "Portfolio metrics for reporting"
    columns:
      - name: total_loans
        description: "Total number of loans in the portfolio"
        tests:
          - not_null
          - accepted_values:
              values: ['>= 0']

