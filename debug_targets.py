import yfinance as yf

assets = ["VOO", "BTC-USD", "ETH-USD", "VUAG.L"]

print(f"{'Ticker':<10} | {'Price':<10} | {'Target Mean':<15} | {'High 52W':<10}")
print("-" * 60)

for t in assets:
    try:
        ticker = yf.Ticker(t)
        info = ticker.info
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        target = info.get('targetMeanPrice')
        high52 = info.get('fiftyTwoWeekHigh')
        
        print(f"{t:<10} | {str(price):<10} | {str(target):<15} | {str(high52):<10}")
    except Exception as e:
        print(f"{t:<10} | Error: {e}")
