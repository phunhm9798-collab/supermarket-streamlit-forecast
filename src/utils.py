import pandas as pd

def clean_data(df):
    # Remove any rows with missing values
    df = df.dropna()
    return df

def transform_data(df):
    # Convert 'Time' column to datetime if it exists
    if 'Time' in df.columns:
        df['Time'] = pd.to_datetime(df['Time'], format="%H:%M:%S")
    return df

def get_unique_values(df, column):
    # Get unique values from a specified column
    return df[column].unique() if column in df.columns else []