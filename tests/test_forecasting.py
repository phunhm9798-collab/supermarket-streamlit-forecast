import pandas as pd
import numpy as np
import pytest
from src.forecasting import (TimeSeriesPreprocessor,
                             ARIMAForecast,
                             HoltWintersForecast,
                             forecast_sales)


@pytest.fixture
def sample_data():
    """Create sample time series data"""
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    values = np.random.normal(loc=100, scale=10, size=30)
    return pd.DataFrame({'Date': dates, 'Total': values})


@pytest.fixture
def preprocessor():
    """Create TimeSeriesPreprocessor instance"""
    return TimeSeriesPreprocessor()


def test_preprocessor_prepare_data(sample_data, preprocessor):
    """Test data preprocessing"""
    prepared = preprocessor.prepare_data(sample_data)

    assert isinstance(prepared, pd.DataFrame)
    assert isinstance(prepared.index, pd.DatetimeIndex)
    assert prepared.shape[1] == 1
    assert not prepared.isnull().any().any()


def test_preprocessor_invalid_date(preprocessor):
    """Test handling of invalid dates"""
    bad_data = pd.DataFrame({
        'Date': ['invalid', '2023-01-01'],
        'Total': [100, 200]
    })

    with pytest.raises(ValueError):
        preprocessor.prepare_data(bad_data)


def test_arima_forecast(sample_data):
    """Test ARIMA forecasting"""
    periods = 7
    forecast = forecast_sales(sample_data, periods=periods, method='arima')

    assert isinstance(forecast, pd.Series)
    assert len(forecast) == periods
    assert not np.isnan(forecast).any()


def test_holtwinters_forecast(sample_data):
    """Test Holt-Winters forecasting"""
    periods = 7
    forecast = forecast_sales(
        sample_data, periods=periods, method='holtwinters')

    assert isinstance(forecast, pd.Series)
    assert len(forecast) == periods
    assert not np.isnan(forecast).any()


def test_forecast_with_missing_data():
    """Test forecasting with missing data"""
    # Create data with gaps
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    values = np.random.normal(loc=100, scale=10, size=30)
    values[5:10] = np.nan

    df = pd.DataFrame({'Date': dates, 'Total': values})

    # Should not raise and should return valid forecast
    forecast = forecast_sales(df, periods=7)
    assert not np.isnan(forecast).any()


def test_model_fitting():
    """Test model fitting process"""
    # Create simple trend data
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
    values = np.arange(30) + np.random.normal(0, 1, 30)
    df = pd.DataFrame({'Date': dates, 'Total': values})

    # Prepare data
    prepared = TimeSeriesPreprocessor().prepare_data(df)

    # Test ARIMA
    arima = ARIMAForecast(prepared)
    arima.fit()
    assert arima.fitted

    # Test Holt-Winters
    hw = HoltWintersForecast(prepared)
    hw.fit()
    assert hw.fitted


def test_empty_data():
    """Test handling of empty DataFrame"""
    empty_df = pd.DataFrame(columns=['Date', 'Total'])

    with pytest.raises(ValueError):
        forecast_sales(empty_df)


def test_forecast_values_reasonable(sample_data):
    """Test if forecasted values are within reasonable bounds"""
    forecast = forecast_sales(sample_data, periods=7)

    # Check if forecasts are within 3 standard deviations of historical data
    historical_std = sample_data['Total'].std()
    historical_mean = sample_data['Total'].mean()

    assert all(abs(x - historical_mean) <= 3 *
               historical_std for x in forecast)
