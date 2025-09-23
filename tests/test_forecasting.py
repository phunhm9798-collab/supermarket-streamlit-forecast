import pandas as pd
import pytest
from src.forecasting import forecast_sales

# Sample data for testing
sample_data = {
    'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
    'Total': [200, 220, 250, 270, 300, 320, 350, 370, 400, 450]
}
df = pd.DataFrame(sample_data)

def test_forecast_sales():
    # Test the forecasting function
    forecasted_values = forecast_sales(df, periods=5)
    
    # Check if the length of forecasted values is correct
    assert len(forecasted_values) == 5
    
    # Check if the forecasted values are numeric
    assert all(isinstance(value, (int, float)) for value in forecasted_values)

def test_forecast_sales_with_empty_data():
    # Test the forecasting function with empty DataFrame
    empty_df = pd.DataFrame(columns=['Date', 'Total'])
    forecasted_values = forecast_sales(empty_df, periods=5)
    
    # Check if the forecasted values are empty
    assert len(forecasted_values) == 0

def test_forecast_sales_with_insufficient_data():
    # Test the forecasting function with insufficient data
    insufficient_data = {
        'Date': pd.date_range(start='2023-01-01', periods=2, freq='D'),
        'Total': [200, 220]
    }
    df_insufficient = pd.DataFrame(insufficient_data)
    forecasted_values = forecast_sales(df_insufficient, periods=5)
    
    # Check if the forecasted values are numeric
    assert all(isinstance(value, (int, float)) for value in forecasted_values) or len(forecasted_values) == 0