import pandas as pd


def load_data(file_path):
    df = pd.read_excel(
        io=file_path,
        engine='openpyxl',
        sheet_name='Sales',
        skiprows=3,
        usecols='B:R',
        nrows=1000,
    )
    return df


def preprocess_data(df):
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    return df


def get_sales_data(file_path):
    df = load_data(file_path)
    df = preprocess_data(df)
    return df
