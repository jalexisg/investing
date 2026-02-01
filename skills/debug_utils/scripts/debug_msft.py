import yfinance as yf
import pandas as pd

def debug_msft():
    ticker = yf.Ticker("MSFT")
    info = ticker.info
    
    print("--- MSFT Info ---")
    print(f"Current Price: {info.get('currentPrice')}")
    print(f"Trailing EPS: {info.get('trailingEps')}")
    print(f"Trailing PE: {info.get('trailingPE')}")
    print(f"Forward PE: {info.get('forwardPE')}")
    print(f"Target Mean Price: {info.get('targetMeanPrice')}")
    
    # Historical PE Calc
    fin = ticker.financials
    if 'Basic EPS' in fin.index:
        eps_series = fin.loc['Basic EPS']
        print("\nHistorical EPS:")
        print(eps_series)
        
        history = ticker.history(period="5y")
        pe_values = []
        print("\nHistorical PE Points:")
        for date, eps in eps_series.items():
            # Convertir fecha de reporte a timestamp con timezone
            ts = pd.Timestamp(date).tz_localize('America/New_York') if pd.Timestamp(date).tz is None else pd.Timestamp(date)
            # Asegurar que history index tiene timezone (yfinance lo devuelve con tz)
            if history.index.tz is None:
                history.index = history.index.tz_localize('America/New_York')
                
            mask = (history.index <= ts)
            if mask.any():
                price = history.loc[mask].iloc[-1]['Close']
                pe = price / eps
                print(f"Date: {date}, Price: {price:.2f}, EPS: {eps}, PE: {pe:.2f}")
                pe_values.append(pe)
        
        if pe_values:
            avg_pe = sum(pe_values) / len(pe_values)
            print(f"\nCalculated 5y Avg PE: {avg_pe:.2f}")
            fair_value = info.get('trailingEps') * avg_pe
            print(f"Calculated Fair Value (EPS * AvgPE): {fair_value:.2f}")
    else:
        print("No Basic EPS found")

debug_msft()
