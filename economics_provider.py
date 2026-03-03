import yfinance as yf
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from ecocal import Calendar

@st.cache_data(ttl=1800) # 30 min cache
def get_market_summary():
    """Fetches major market indices for the ticker tape."""
    major_tickers = {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ",
        "^DJI": "Dow Jones",
        "GC=F": "Gold",
        "CL=F": "Crude Oil",
        "BTC-USD": "Bitcoin",
        "EURUSD=X": "EUR/USD"
    }
    
    data = []
    for symbol, name in major_tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            # Use history for last 2 days to get change
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_price = hist['Close'].iloc[-1]
                change = curr_price - prev_close
                change_pct = (change / prev_close) * 100
                data.append({
                    "symbol": name,
                    "price": round(curr_price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2)
                })
        except Exception as e:
            print(f"Error fetching summary for {symbol}: {e}")
    return data

@st.cache_data(ttl=3600)
def get_economic_calendar():
    """Fetches real economic calendar data using ecocal."""
    try:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=7)
        
        # Instantiate ecocal Calendar
        ec = Calendar(
            startHorizon=start_date.strftime("%Y-%m-%d"),
            endHorizon=end_date.strftime("%Y-%m-%d"),
            withDetails=True,
            nbThreads=10,
            withProgressBar=False
        )
        
        df = ec.detailedCalendar
        if df is None or df.empty:
            return pd.DataFrame(columns=["Time", "Currency", "Event", "Importance", "Actual", "Forecast", "Prev"])
        
        # Map columns
        # Start format: '03/03/2026 00:01:00'
        def extract_time(start_str):
            try:
                return start_str.split(" ")[1][:5]
            except:
                return "-"

        processed_data = []
        for _, row in df.iterrows():
            processed_data.append({
                "Time": extract_time(row.get('Start', '')),
                "Currency": row.get('Currency', '-'),
                "Event": row.get('Name', 'Unknown Event'),
                "Importance": str(row.get('Impact', 'Low')).capitalize(),
                "Actual": str(row.get('actual')) if row.get('actual') is not None else "-",
                "Forecast": str(row.get('consensus')) if row.get('consensus') is not None else "-",
                "Prev": str(row.get('previous')) if row.get('previous') is not None else "-"
            })
            
        return pd.DataFrame(processed_data)
        
    except Exception as e:
        print(f"Error fetching economic calendar: {e}")
        # Fallback to empty DF with correct columns
        return pd.DataFrame(columns=["Time", "Currency", "Event", "Importance", "Actual", "Forecast", "Prev"])
