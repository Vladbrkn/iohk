# This script demonstrates a mock validation workflow using Great Expectations - it is a conceptual showcase of data validation steps.
# Note: this code will not run as-is, as it assumes the Great Expectations package and any helper functions are installed and configured.

import __init__
from great_expectations_helper import validateDifferentSources

def run_validation():
    # Parameters for the source data validation suite
    expectation_info = {
        "suite_name": "upstream_validation_check",  # Name of the expectation suite
        "asset_name": "source_loans",               # Reference name for source asset
        "db": "raw",                                # Database name containing source data
        "sql_file_path": "code/great_expectations/sql/source_loans.sql"  
    }

    # Parameters for the validation against the master data
    validation_info = {
        "checkpoint_name": "compare_master_data_source_loans",  # Checkpoint name for validation
        "asset_name": "master_data",                            # Reference name for master data asset
        "db": "warehouse",                                      # Database name for master data
        "sql_file_path": "code/great_expectations/sql/master_data.sql" 
    }

    # Initialize the validation process for comparing source data with master data
    upstream_validation = validateDifferentSources(expectation_info, validation_info)
    upstream_validation.setup_expectation_suite()  # Set up the expectation suite

    # Retrieve the validation DataFrame containing the source data for comparison
    validation_df = upstream_validation.get_expectation_data_df()

    # Get the Great Expectations validator object
    validator = upstream_validation.validator

    # Define a margin of error for value comparisons
    MARGIN_OF_ERROR = 5

    # Expectations:
    # 1. Expect the number of rows in the data to match the expected row count from the source
    validator.expect_table_row_count_to_equal(validation_df.shape[0])

    # 2. Ensure critical columns are non-null
    validator.expect_column_values_to_not_be_null("loan_id")  # loan_id column should not contain null values
    validator.expect_column_values_to_be_in_set("loan_id", validation_df.get_column("loan_id"))  # Validate loan_id exists in master data
    validator.expect_column_values_to_be_in_set("borrower_id", validation_df.get_column("borrower_id"))  # Validate borrower_id integrity
    
    # 3. Verify principal_amount is within an expected range
    validator.expect_column_values_to_be_between("principal_amount", min_value=100, max_value=100000)

    # Save the expectation suite, keeping any failed expectations for review
    validator.save_expectation_suite(discard_failed_expectations=False)

    # Build and execute the validation checkpoint for comparison
    upstream_validation.build_and_run_validation_checkpoint()

if __name__ == "__main__":
    run_validation()

# Note: Alternatively, SQL-level aggregations can be performed to improve script efficiency,
# in which case we would use `expect_column_unique_value_count_to_be_between` for all validations.
