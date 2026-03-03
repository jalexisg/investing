import yfinance as yf
import pandas as pd
import numpy as np

def calculate_technical_summary(ticker_symbol):
    """
    Calculates a technical summary based on multiple indicators.
    Returns: 'Strong Buy', 'Buy', 'Neutral', 'Sell', 'Strong Sell'
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="6mo")
        if len(hist) < 200:
            return "Neutro (Datos insuficientes)"

        close = hist['Close']
        
        # 1. Moving Averages
        ma20 = close.rolling(window=20).mean().iloc[-1]
        ma50 = close.rolling(window=50).mean().iloc[-1]
        ma200 = close.rolling(window=200).mean().iloc[-1]
        current_price = close.iloc[-1]
        
        scores = 0
        
        # Score based on price vs MAs
        if current_price > ma20: scores += 1
        else: scores -= 1
        
        if current_price > ma50: scores += 1
        else: scores -= 1
        
        if current_price > ma200: scores += 1
        else: scores -= 1
        
        # 2. RSI (Relative Strength Index)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        if rsi < 30: scores += 2 # Oversold (Buy signal)
        elif rsi > 70: scores -= 2 # Overbought (Sell signal)
        
        # Final Signal Logic
        if scores >= 3: return "Compra Fuerte"
        elif scores >= 1: return "Compra"
        elif scores <= -3: return "Venta Fuerte"
        elif scores <= -1: return "Venta"
        else: return "Neutral"
        
    except Exception as e:
        print(f"Error calculating technicals for {ticker_symbol}: {e}")
        return "N/A"
