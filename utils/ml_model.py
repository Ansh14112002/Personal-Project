import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Flask applications
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64

def fetch_stock_data(symbol: str, period: str = '1y') -> pd.DataFrame:
    """
    Fetch historical stock data using yfinance.
    Raises a ValueError if no data is found.
    """
    try:
        data = yf.download(symbol, period=period)
        if data.empty:
            raise ValueError(f"No data found for {symbol}. Please check the ticker symbol.")
        return data
    except Exception as e:
        raise ValueError(f"Failed to fetch stock data: {str(e)}")

def generate_forecast_plot(dates: pd.Series, actual: pd.Series, future_dates: pd.Series, predictions: list, symbol: str) -> str:
    """
    Generate a forecast plot and return it as a base64-encoded PNG image.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, actual, label='Historical Price')
    ax.plot(future_dates, predictions, label='Predicted Price (Next 30 Days)', linestyle='--')
    ax.set_title(f"{symbol.upper()} - 30 Day Price Forecast")
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (₹)')
    ax.legend()
    fig.tight_layout()

    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def train_predict_stock(symbol: str) -> tuple:
    """
    Train a Linear Regression model on historical stock data and forecast the next 30 days.
    Returns:
        - List of predicted prices
        - Base64 string of the forecast plot
    """
    try:
        # Step 1: Fetch and prepare data
        data = fetch_stock_data(symbol)
        data = data.reset_index()
        data['Date_ordinal'] = data['Date'].apply(lambda date: date.toordinal())

        X = data[['Date_ordinal']]
        y = data['Close']

        # Step 2: Train Linear Regression model
        model = LinearRegression()
        model.fit(X, y)

        # Step 3: Forecast future prices
        last_date = data['Date'].max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30)
        future_ordinals = future_dates.to_series().apply(lambda x: x.toordinal()).to_frame(name='Date_ordinal')
        predictions = model.predict(future_ordinals)

        # Step 4: Generate forecast plot
        forecast_image = generate_forecast_plot(data['Date'], y, future_dates, predictions, symbol)

        return predictions.flatten().tolist(), forecast_image

    except ValueError as ve:
        raise ve  # Re-raise custom errors for clean handling in Flask
    except Exception as e:
        raise ValueError(f"Forecasting failed: {str(e)}")
