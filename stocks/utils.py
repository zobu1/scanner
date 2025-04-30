# stocks/utils.py
from django.db import connection
import pandas as pd

def get_last_n_days_history(stock_id, n):
    """
    Retrieves the last `n` days of historical records for a given stock 
    using a raw SQL query (prepared statement).
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT date, price
            FROM stocks_stockhistory
            WHERE stock_id = %s
            ORDER BY date DESC
            LIMIT %s
        """, [stock_id, n])  
        rows = cursor.fetchall() 
    df = pd.DataFrame(rows, columns=['date', 'price'])
    # Sort ascending by date if needed
    df = df.sort_values(by='date')
    return df.reset_index(drop=True)

def compute_rsi(prices, period=10):
    """
    Compute RSI using a rolling window average of gains and losses.
    This function requires at least period+1 price points.
    """
    if len(prices) < period + 1:
        return None

    # Ensure the prices are in ascending order (oldest first, newest last)
    series = pd.Series(prices)
    delta = series.diff().dropna()  
    
    # Calculate gains and losses
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    # Calculate the rolling average of gains and losses
    avg_gain = gain.rolling(window=period, min_periods=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period, min_periods=period).mean().iloc[-1]
    
    if avg_loss == 0:
        return 100  
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_cumulative_return(prices):
    """
    (last_price - first_price) / first_price
    """
    if len(prices) < 5:
        return None
    return (prices[-1] - prices[0]) / prices[0]

def compute_average_return(prices):
    """
    Average daily return over the last 5 days.
    """
    if len(prices) < 5:
        return None
    daily_returns = []
    for i in range(1, len(prices)):
        daily_returns.append((prices[i] - prices[i-1]) / prices[i-1])
    return sum(daily_returns) / len(daily_returns)
