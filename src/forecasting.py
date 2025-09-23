import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import numpy as np

def prepare_data(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df.resample('D').sum()  # Resample to daily frequency

def forecast_sales(df, periods=30):
    df_prepared = prepare_data(df)
    model = ExponentialSmoothing(df_prepared['Total'], trend='add', seasonal='add', seasonal_periods=12)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=periods)
    return forecast

def get_forecast(df, periods=30):
    forecast = forecast_sales(df, periods)
    forecast_df = pd.DataFrame(forecast, columns=['Forecasted Sales'])
    forecast_df.index.name = 'Date'
    return forecast_df.reset_index()