import pandas as pd
import numpy as np

def calculate_terms(df):
    """
    Calculate the expected and actual terms for each loan in both days and months.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing loan data.
    
    Returns:
    pd.DataFrame: The DataFrame with added columns for expected and actual terms in days and months.
    """
    
    df['expected_term_days'] = (df['maturity_date'] - df['issue_date']).dt.days
    df['expected_term_months'] = df['expected_term_days'] / 30

    df['actual_term_days'] = np.where(
        df['closing_date'].notna(),
        (df['closing_date'] - df['issue_date']).dt.days,
        np.nan 
    )
    df['actual_term_months'] = df['actual_term_days'] / 30
    
    return df

def calculate_write_off_rate(df):
    """
    Calculate the write-off rate based on the write-off amount and the principal amount.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing loan data, specifically 'write_off_amount' and 'principal_amount'.
    
    Returns:
    float: The write-off rate as a percentage.
    """

    total_write_off_amount = df['write_off_amount_usd'].sum()
    total_principal_amount = df['principal_amount_usd'].sum()
    
    if total_principal_amount > 0: 
        write_off_rate = (total_write_off_amount / total_principal_amount) * 100
    else:
        write_off_rate = 0.0
    
    return write_off_rate

def calculate_interest_metrics(df):
    """
    Calculate the expected interest, expected daily interest, and actual interest for each loan.
    
    Formulae:
    1. expected_interest = principal_amount * interest_rate
    2. expected_interest_daily = expected_interest / expected_term_days
    3. actual_interest = expected_interest_daily * actual_term_days
    
    Parameters:
    df (pd.DataFrame): The input DataFrame containing loan data, specifically 'principal_amount', 'interest_rate',
                       'expected_term_days', and 'actual_term_days'.
    
    Returns:
    pd.DataFrame: The DataFrame with the added columns 'expected_interest', 'expected_interest_daily', and 'actual_interest'.
    """

    df['expected_interest'] = df['principal_amount_usd'] * df['interest_rate']
  
    df['expected_interest_daily'] = df['expected_interest'] / df['expected_term_days']
    
    df['actual_interest'] = df['expected_interest_daily'] * df['actual_term_days']
    
    return df

def calculate_avg_days_in_arrears(df):
    """
    Calculate the average days in arrears based on the difference between
    the closing date and maturity date for each loan in the dataset.
    
    Parameters:
    df (pd.DataFrame): DataFrame containing loan information, with columns
                       'closing_date' and 'maturity_date' in datetime format.
    
    Returns:
    float: The average days in arrears across all loans with valid closing dates.
           Returns NaN if no loans have a valid closing date.
    """

    df['days_in_arrears'] = (df['closing_date'] - df['maturity_date']).dt.days

    # Exclude rows with missing or negative days in arrears
    valid_arrears_days = df['days_in_arrears'].dropna()
    
    avg_days_in_arrears = valid_arrears_days.mean()
    
    return avg_days_in_arrears