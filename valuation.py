import yfinance as yf
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour to avoid rate limits
def get_historical_pe(ticker_symbol):
    """
    Calculates the average P/E of the last 5 years using historical data.
    Returns (avg_pe, method_used)
    """
    try:
        t = yf.Ticker(ticker_symbol)
        
        # 1. Try to get historical EPS
        fin = t.financials
        if 'Basic EPS' not in fin.index:
            # Try with 'Diluted EPS' if Basic is not available
            if 'Diluted EPS' in fin.index:
                eps_series = fin.loc['Diluted EPS']
            else:
                return None, "No historical EPS"
        else:
            eps_series = fin.loc['Basic EPS']
            
        # 2. Get historical prices for report dates
        pe_values = []
        history = t.history(period="5y")
        
        if history.empty:
            return None, "No price history"

        for date, eps in eps_series.items():
            try:
                ts = pd.Timestamp(date)
                # Robust method: find price on or before report date
                mask = (history.index <= ts)
                if mask.any():
                    price = history.loc[mask].iloc[-1]['Close']
                    if eps > 0:  # Avoid division by zero or weird negative P/Es for average
                        pe = price / eps
                        # Filter extreme outliers
                        if 0 < pe < 200:
                            pe_values.append(pe)
            except Exception:
                continue
                
        if pe_values:
            return sum(pe_values) / len(pe_values), "5y Historical Avg"
        
        return None, "Insufficient data"
        
    except Exception as e:
        print(f"Error calculating historical PE for {ticker_symbol}: {e}")
        return None, "Error"

def calculate_composite_fair_value(current_price, info, ticker_symbol):
    """
    Calculates a composite Fair Value using multiple models.
    """
    eps = info.get('trailingEps')
    pe_ratio = info.get('trailingPE')
    peg_ratio = info.get('pegRatio')
    target_price = info.get('targetMeanPrice')
    
    models = {}
    
    # 1. Analyst Target Price
    if target_price:
        models['Analyst Target'] = target_price
        
    # 2. Graham Formula (Modified): V = EPS * (8.5 + 2g)
    if eps and eps > 0 and pe_ratio and peg_ratio and peg_ratio > 0:
        try:
            expected_growth = pe_ratio / peg_ratio
            g = min(expected_growth, 25) 
            graham_value = eps * (8.5 + 2 * g)
            models['Graham Formula'] = graham_value
        except Exception:
            pass
            
    # 3. Historical PE
    hist_pe, _ = get_historical_pe(ticker_symbol)
    if hist_pe and eps:
        models['Historical PE'] = eps * hist_pe

    # Composite Fair Value
    if models:
        valid_values = [v for v in models.values() if v is not None and v > 0]
        if valid_values:
            fair_value = sum(valid_values) / len(valid_values)
            model_details = "\n".join([f"{k}: ${v:.2f}" for k, v in models.items()])
        else:
            fair_value = None
            model_details = "No valid models"
    else:
        # Fallback: Trailing PE * EPS
        if eps and pe_ratio:
            fair_value = eps * pe_ratio
            model_details = "Fallback: Trailing PE"
        else:
            fair_value = None
            model_details = "Insufficient Data"

    return fair_value, model_details
