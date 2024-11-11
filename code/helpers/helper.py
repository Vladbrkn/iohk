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

    total_write_off_amount = df['write_off_amount'].sum()
    total_principal_amount = df['principal_amount'].sum()
    
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

    df['expected_interest'] = df['principal_amount'] * df['interest_rate']
  
    df['expected_interest_daily'] = df['expected_interest'] / df['expected_term_days']
    
    df['actual_interest'] = df['expected_interest_daily'] * df['actual_term_days']
    
    return df