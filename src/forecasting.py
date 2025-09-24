import pandas as pd
import numpy as np
import streamlit as st
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
import datetime
from typing import Union, Tuple, Optional


class TimeSeriesPreprocessor:
    """Handles data preprocessing for time series forecasting"""

    @staticmethod
    def prepare_data(df: pd.DataFrame,
                     date_col: str = 'Date',
                     value_col: str = 'Total',
                     freq: str = 'D') -> pd.DataFrame:
        """
        Prepare time series data for forecasting.
        Returns DataFrame with datetime index and single value column.
        """
        if date_col not in df.columns:
            raise KeyError(f"Expected date column '{date_col}' in dataframe")

        df = df.copy()
        # Parse dates
        df[date_col] = pd.to_datetime(
            df[date_col].astype(str), errors='coerce')
        if df[date_col].isna().all():
            raise ValueError(f"No valid dates in column '{date_col}'")

        # Clean and set index
        df = df.loc[df[date_col].notna()]
        df.set_index(date_col, inplace=True)

        # Select value column
        if value_col not in df.columns:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                raise ValueError("No numeric columns found for forecasting")
            value_col = numeric_cols[0]

        # Prepare series
        series = pd.to_numeric(df[value_col], errors='coerce')
        series = series.resample(freq).sum()
        series = series.fillna(method='ffill').fillna(0.0)

        return series.to_frame(name=value_col)


class ForecastModel:
    """Base class for forecasting models"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.model = None
        self.fitted = False

    def fit(self):
        """Fit the model - implemented by subclasses"""
        raise NotImplementedError

    def predict(self, periods: int) -> pd.Series:
        """Generate forecast - implemented by subclasses"""
        raise NotImplementedError


# ...existing code for TimeSeriesPreprocessor and ForecastModel classes...

class ARIMAForecast(ForecastModel):
    """ARIMA forecasting model with fixed parameters"""

    def fit(self) -> None:
        """Fit ARIMA model with standard parameters"""
        series = self.data.iloc[:, 0]

        # Use standard SARIMA parameters suitable for daily data
        # (1,1,1) for trend, weekly seasonality
        self.model = SARIMAX(series,
                             order=(1, 1, 1),
                             seasonal_order=(1, 1, 1, 7))
        try:
            self.model = self.model.fit(disp=False)
            self.fitted = True
        except:
            # If SARIMA fails, try simple ARIMA(1,1,1)
            self.model = SARIMAX(series,
                                 order=(1, 1, 1))
            try:
                self.model = self.model.fit(disp=False)
                self.fitted = True
            except:
                # Both models failed - will use naive forecast in predict()
                self.fitted = False

    def predict(self, periods: int) -> pd.Series:
        """Generate forecast using fitted ARIMA model"""
        if not self.fitted:
            # Fallback to naive forecast
            last_value = float(self.data.iloc[-1, 0])
            last_date = self.data.index[-1]
            dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                  periods=periods,
                                  freq='D')
            return pd.Series([last_value] * periods, index=dates)

        try:
            forecast = self.model.forecast(periods)
            return forecast
        except Exception:
            # Fallback to naive forecast if prediction fails
            last_value = float(self.data.iloc[-1, 0])
            last_date = self.data.index[-1]
            dates = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                  periods=periods,
                                  freq='D')
            return pd.Series([last_value] * periods, index=dates)


class HoltWintersForecast(ForecastModel):
    """Holt-Winters forecasting model"""

    def fit(self) -> None:
        """Fit Holt-Winters model with deployment-safe parameters"""
        series = self.data.iloc[:, 0]
        n = len(series)
        seasonal_periods = 7 if n >= 14 else None

        try:
            if seasonal_periods and n >= (seasonal_periods * 2):
                self.model = ExponentialSmoothing(
                    series,
                    trend='add',
                    seasonal='add',
                    seasonal_periods=seasonal_periods,
                    initialization_method='estimated'  # More stable initialization
                )
            else:
                self.model = ExponentialSmoothing(
                    series,
                    trend='add',
                    seasonal=None,
                    initialization_method='estimated'
                )

            # Simplified fit parameters for better deployment compatibility
            self.model = self.model.fit(
                method='least_squares',  # More stable than MLE
                remove_bias=False,
                use_brute=False
            )
            self.fitted = True
        except Exception as e:
            st.warning(f"Using fallback forecast method: {str(e)}")
            self.fitted = False

    def predict(self, periods: int) -> pd.Series:
        """Generate forecast using fitted Holt-Winters model"""
        if not self.fitted:
            return self._naive_forecast(periods)

        try:
            forecast = self.model.forecast(periods)
            # Ensure no negative values in forecast
            forecast = forecast.clip(lower=0)
            return forecast
        except Exception as e:
            st.warning(f"Falling back to naive forecast: {str(e)}")
            return self._naive_forecast(periods)

    def _naive_forecast(self, periods: int) -> pd.Series:
        """Generate naive forecast using last known value"""
        last_value = float(self.data.iloc[-1, 0])
        last_date = self.data.index[-1]
        dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=periods,
            freq='D'
        )
        return pd.Series([last_value] * periods, index=dates)


def forecast_sales(df: pd.DataFrame,
                   periods: int = 30,
                   freq: str = 'D',
                   value_col: str = 'Total',
                   method: str = 'arima') -> pd.Series:
    """
    Generate sales forecast using specified method.

    Parameters:
        df: Input DataFrame with date and value columns
        periods: Number of periods to forecast
        freq: Frequency of the time series
        value_col: Name of the value column
        method: Forecasting method ('arima' or 'holtwinters')

    Returns:
        Forecast as a pandas Series
    """
    # Prepare data
    preprocessor = TimeSeriesPreprocessor()
    prepared_data = preprocessor.prepare_data(df,
                                              value_col=value_col,
                                              freq=freq)

    # Select and fit model
    if method.lower() == 'arima':
        model = ARIMAForecast(prepared_data)
    else:
        model = HoltWintersForecast(prepared_data)

    model.fit()
    return model.predict(periods)


def get_forecast(df: pd.DataFrame,
                 periods: int = 30,
                 freq: str = 'D',
                 value_col: str = 'Total',
                 method: str = 'arima') -> pd.DataFrame:
    """Generate forecast and return as DataFrame with date index"""
    forecast = forecast_sales(df,
                              periods=periods,
                              freq=freq,
                              value_col=value_col,
                              method=method)
    return pd.DataFrame({'Date': forecast.index,
                        'Forecasted Sales': forecast.values})
