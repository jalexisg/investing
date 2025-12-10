import yfinance as yf
import pandas as pd

def test_data(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    print(f"--- {ticker_symbol} ---")
    
    # 1. Info
    info = t.info
    print(f"Current EPS: {info.get('trailingEps')}")
    print(f"Current PE: {info.get('trailingPE')}")
    
    # 2. Financials (for historical EPS)
    print("\nFinancials (EPS):")
    try:
        fin = t.financials
        # Row 'Basic EPS' or similar
        if 'Basic EPS' in fin.index:
            print(fin.loc['Basic EPS'])
        else:
            print("Basic EPS not found in financials index")
            print(fin.index)
    except Exception as e:
        print(f"Error fetching financials: {e}")

    # 3. History (for historical Price)
    print("\nHistory (Price):")
    try:
        hist = t.history(period="5y")
        print(hist['Close'].resample('Y').mean().tail())
    except Exception as e:
        print(f"Error fetching history: {e}")

test_data("AAPL")
