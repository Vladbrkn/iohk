# Swift Loan Data Analysis 

## Project Overview

This project is aimed at providing insights into Swift Loan’s loan portfolio. The primary objective is to analyze the data in order to calculate key performance metrics and provide actionable insights for RealFi’s investment team. Swift Loan is a fintech company seeking $1 million in debt capital, and this analysis forms part of the due diligence process.

## Data Preprocessing and Cleaning

### Overview

As part of the loan data analysis , I have worked on cleaning and preparing the dataset for further analysis. The data includes three primary csv's: **Loans**, **Payments**, and **Borrowers**. 
Each csv was treated as if it were a source table.
Below, I document the key steps taken to inspect, clean, and merge these datasets to ensure consistency and readiness for modeling.

### Data Sources

The datasets were cleaned and merged, with the **Loans** dataset being used as the base table. The data included:

- **Loans**: Contains loan details, with columns `loan_id` and `borrower_id` are the join keys.
- **Payments**: Contains information on payments made for loans, where `loan_id` is the join key.
- **Borrowers**: Contains borrower details, were `borrower_id` is the join key.

### Cleaning Steps

All datasets underwent the same process. Object-type columns that were categorical in nature were converted to categorical columns, while all object-type date columns were converted to `datetime`.

#### Loans Dataset

- **Duplicate and Illogical Maturity Dates**:  
  I identified 12 records where the `maturity_date` was either earlier than the `issue_date` (illogical), or had a `NaT` or impossible date (e.g., `0019-03-20`). As there are 675,767 unique loan IDs in the dataset, I have decided to remove these records for now, though the exact cause of these issues is unclear (whether they are data errors or placeholders).

- **Null Values**:  
  The `borrower_id` column in the Loans dataset has 2,745,040 non-null values out of a total of 2,757,862 records. As this column is essential for joining the Loans dataset to the Borrowers dataset, I will address any missing or null values during the data merge process.

#### Payments Dataset

- **Duplicate Payment Records**:  
  I noticed instances where the same `payment_id` appeared on the same `payment_date` but for different `loan_id` values (e.g., `payment_id` = `U0M4MkYyWjAyUw==`). After reviewing these cases, I decided to retain these records, as they may represent valid scenarios where multiple payments were processed on the same date through batch processing and later manually allocated to different loans.

- **Null Payment Dates**:  
  I decided to drop any records with null `payment_date` values, as a payment should logically have a corresponding date. Keeping these null entries could complicate further analysis and metric calculations.

#### Borrowers Dataset

- **Handling Duplicates**:  
  The Borrowers dataset contains 4,282,097 records with 450,707 unique `borrower_id`. Since the dataset includes multiple snapshots per borrower (due to the `as_of_datetime`), I ordered the dataset by this timestamp to keep only the most recent record for each borrower. 

- **Illogical Date of Birth Values**:  
  After processing, I found that 154 rows had a `date_of_birth` before 1924, which is illogical given the current year and would imply the borrower is 100 years old. Additionally, 1,360 rows had `date_of_birth` values after 2005, suggesting the borrower was under 18 at the time of loan issuance (the maximum `issue_date` in the Loans dataset is 2023-07-01). I am assuming that, due to business requirements or qualifying criteria, any person younger than 18 cannot apply for a loan .Both of these scenarios are invalid, so I removed these records:
  - Records with `date_of_birth` before 1924 were removed, accounting for ~0.03% of the data.
  - Records with `date_of_birth` after 2005 were removed, accounting for ~0.3% of the data.

#### Master Dataset

- **Merging Data**:  
  After cleaning and processing the three individual datasets, I merged them into a single master dataset. 

- **Null Borrower IDs**:  
  In the merged dataset, there were 12,594 records with a `null` `borrower_id` but a valid `loan_id`. Since these account for ~1.9% of the data, I decided to remove these entries for the sake of simplicity. The impact of removing these records on metrics (e.g., write-off rate) is still to be determined.

- **Multiple Borrower IDs per Loan**:  
  I also identified instances where a single `loan_id` was associated with multiple `borrower_id`s (e.g., loan ID `S0VfS1VfQ01EVzk2Mw==`). This is illogical and suggests potential data corruption or logical reasons for the change of borrower ID. I have decided not to handle these cases yet and will revisit them during the metric calculation phase.

- **Anomalous Records**:  
  Certain loans have a snapshot date of 2024-10-01, though they were issued in 2022 with an expected maturity within that same year. These records lack associated payments, `closing_date`, or `write_off_date`, making it challenging to determine the appropriate handling without additional business context.

- **Currency Consistency**:  
  While it is understood that payment currency should align with the loan currency, this aspect has been excluded from the analysis for the purpose of this assignment.

## Metrics

### **Data Preparation**:  
  A copy of the master dataset was created as a working DataFrame, referred to here as `metrics_df`, to perform calculations without altering the original master data.

### **Helper Functions**:  
  Developed and added helper functions to calculate various metrics, including:
  - **Expected Term and Actual Term**: Calculated in both days and months.
  - **Write-Off Rate**: A metric assessing the proportion of loans that have been written off.
  - **Interest Metrics**: Used to calculate gross yield, representing the return generated by the loans.

#### **Write-Off Rate Calculation**:
  - While calculating the write-off rate, I found a record with a future maturity date (`loan_id`: VUdfS1VfNDI2NQ==) of `2200-01-20`. This was deemed erroneous and removed.
  - A helper function was created to automate the write-off rate calculation. Only the latest snapshot for each `loan_id` was retained, as only the final `write_off_amount` and `principal_amount` are needed.
  - Write-off rate formula:
  $$ \text{Write-Off Rate} = \left( \frac{\text{Total Write-Offs}}{\text{Total Charges}} \right) \times 100 $$
  - **Total Write-Offs**: The sum of write off amounts.
  - **Total Charges**: Represented by the `principal_amount` of the loans.

### **Gross Yield Calculation**:
  - Gross yield was calculated as follows:
  $$ \text{Gross Yield} = \left( \frac{\text{Gross Income}}{\text{Total Investment}} \right) \times 100 $$
  - **Gross Income**: The total income generated from the loans before expenses.
  - **Total Investment**: Represented by the `principal_amount` of the loans.

  - Specifically:
    - **Total Investment** = `principal_amount`.
    - **Gross Income** = `principal_amount` * `actual_interest`.

- **Considerations for Interest Calculation**:
  - Given that `interest_rate` represents the expected interest rate over the full loan term and that penalties and fees are typically excluded from gross yield, the following approach was taken:
    - **Actual Term** was calculated as the difference between `closing_date` and `issue_date` (in days).
    - **Actual Interest Earned** was calculated as follows: $$ \text{Actual Interest Earned} = \text{expected\_interest\_daily} \times \text{actual\_term\_days} $$
      - Where `expected_interest_daily` is computed as:
      $$ \text{expected\_interest\_daily} = \left( \frac{\text{expected\_interest}}{\text{expected\_term\_days}} \right) \times 100 $$

- **Exclusion of Fees and Penalties**:
  - Industry sources suggest that penalties and fees should be tracked separately and excluded from gross yield, as they are typically considered operational revenue rather than a part of standard yield calculations. For this reason, any penalties and fees incurred after the maturity date were excluded from the gross yield calculation, which focuses solely on interest earned from the principal amount during the active loan period.

### **Collections Rate**:
  At this stage, I will not be calculating the collections rate, as the payment structures and associated details are not fully understood in this dataset. Typically, the collections rate is calculated as the ratio of payments received to total outstanding balances.

  It is standard industry practice to exclude written-off loans when calculating the collections rate. This is because loans that have been written off are generally considered uncollectible, and including them would result in an inaccurate and understated collections rate by adding balances that are no longer realistically collectible.

### **Average Days in Arrears**:
  - Average days in arrears was calculated as follows:
  $$ \text{avg\_days\_in\_arrears} = \frac{\sum (\text{closing\_date} - \text{maturity\_date})}{n} $$

  Where:
  - `closing_date` is the date when the loan was closed.
  - `maturity_date` is the date when the loan was due.
  - \( n \) is the number of valid entries (i.e., entries with non-negative days in arrears).

  The calculation of average days in arrears typically uses the difference between the `closing_date` or `as_of_datetime` and the `default_date`. However, in this dataset, there are instances where the `default_date` is later than both the `maturity_date` and `write_off_date`, which creates some confusion in terms of logical consistency.

  For example, `loan_id`: `S0VfS1VfMjg4MjI0` exhibits this issue.

  Due to this inconsistency, I have decided to calculate average days in arrears as the difference between the `closing_date` and the `maturity_date`. This approach is based on the assumption that the loan should be considered in arrears from the point it matures until it is either closed or written off.

## Mock dbt-SQL Files

I have added mock dbt-SQL files to this documentation to demonstrate how the data modeling process might look in dbt. These files serve as a representation of how the SQL queries could be structured in a dbt project. Since none of the SQL queries have been validated, these are intended to be seen as pseudo-code or templates for the potential production-ready code and not final implementations.

### What is dbt?
dbt (Data Build Tool) is an open-source data transformation tool used by data analysts and engineers to automate the transformation of raw data into clean, structured, and analytical datasets. dbt allows teams to write SQL-based transformation queries, version control these queries, and deploy them to a data warehouse. It also supports automated testing and documentation, ensuring data consistency and quality throughout the transformation process. The main advantages of dbt include:

- **SQL-based transformations**: dbt allows you to write SQL queries that transform raw data into useful, analytical datasets.
- **Version control**: dbt integrates well with Git for version control, ensuring that changes to transformation logic can be tracked and managed over time.
- **Testing and documentation**: dbt makes it easy to implement tests and auto-generate documentation for your models, increasing collaboration and data governance within the team.

### Bronze, Silver, and Gold Models
In dbt, the data modeling process is typically structured into three layers: bronze, silver, and gold. These layers represent the stages of data processing, from raw data to final analytical datasets.

#### Bronze Models (Raw Data)
Bronze models are the first layer and contain raw data with minimal transformations. They serve as a foundation for further processing and refinement. The bronze layer focuses on standardizing formats, such as data types and date fields, and basic data cleansing, such as removing duplicates and handling null values. In this case:

- `bronze_loans`: Loads and standardizes loan data.
- `bronze_payments`: Loads and standardizes payment data.
- `bronze_borrowers`: Loads and standardizes borrower data.

#### Silver Models (Enriched Data)
Silver models build upon the bronze layer by applying business rules and aggregating data to create a more refined view of the dataset. This layer includes calculations and transformations such as calculating terms (expected vs. actual), interest metrics, and arrears metrics, while preserving the loan and payment granularity. Here:

- `silver_loans`: Enriches loan data with metrics like `expected_term_days`, `actual_term_days`, `expected_interest`, and `days_in_arrears`.
- Additional calculations, such as gross yield, collection rate, and write-off rates, are added at this stage.

#### Gold Models (Final Analytical Datasets)
Gold models are the final layer and contain data ready for analysis and reporting. These models aggregate and summarize key performance metrics across the entire portfolio, creating a single view of the data at the highest level. In this case:

- `gold_portfolio_metrics`: Aggregates metrics like total loans, portfolio write-off rate, and gross yield.
  
### dbt Tests
To ensure data quality and consistency, dbt allows you to define tests on your models. Below are examples of tests that could be implemented for this project:

- **Not Null Constraints**: Ensures critical columns, like `principal_amount` and `loan_id`, are populated.
- **Accepted Values**: Validates logical relationships, such as `maturity_date` being greater than or equal to `issue_date`.

 
 *To do:
 - dbt documentation 
 - great_expectations
