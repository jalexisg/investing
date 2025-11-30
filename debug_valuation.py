import yfinance as yf
import pandas as pd

def debug_valuation(ticker_symbol):
    print(f"--- Debugging Valuation for {ticker_symbol} ---")
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    
    current_price = info.get('currentPrice')
    eps = info.get('trailingEps')
    pe_ratio = info.get('trailingPE')
    peg_ratio = info.get('pegRatio')
    book_value = info.get('bookValue')
    target_price = info.get('targetMeanPrice')
    
    print(f"Price: {current_price}")
    print(f"EPS: {eps}")
    print(f"PE: {pe_ratio}")
    print(f"PEG: {peg_ratio}")
    print(f"Book Value: {book_value}")
    print(f"Target Price: {target_price}")
    
    models = {}
    
    # 1. Analyst Target
    if target_price:
        models['Analyst Target'] = target_price
        
    # 2. Graham Formula
    if eps and pe_ratio and peg_ratio:
        expected_growth = pe_ratio / peg_ratio
        g = min(expected_growth, 25)
        print(f"Derived Growth (g): {g:.2f}%")
        graham_value = eps * (8.5 + 2 * g)
        models['Graham Formula'] = graham_value
        
    # 3. Graham Number
    if eps and book_value:
        graham_number = (22.5 * eps * book_value) ** 0.5
        models['Graham Number'] = graham_number
        
    # 4. Historical PE (Simulated for debug)
    # Assuming we can't easily run the full historical function here without copying it,
    # let's just see what the others give. The historical one we saw before was ~464.
    # models['Historical PE'] = 464.0 # Placeholder based on previous turn
    
    print("\n--- Model Results ---")
    for k, v in models.items():
        print(f"{k}: ${v:.2f}")
        
    avg = sum(models.values()) / len(models)
    print(f"\nComposite Average: ${avg:.2f}")
    print(f"Status: {'Undervalued' if current_price < avg else 'Overvalued'}")

debug_valuation("MSFT")
