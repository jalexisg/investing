import yfinance as yf
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from valuation import calculate_composite_fair_value

from technical_provider import calculate_technical_summary

@st.cache_data(ttl=900)  # 15 min cache
def get_stock_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None

        # Calculate Fair Value
        fair_value, model_details = calculate_composite_fair_value(current_price, info, ticker_symbol)
        
        # Calculate Technical Summary
        technical_summary = calculate_technical_summary(ticker_symbol)

        # Status & Potential
        if fair_value:
            potential = ((fair_value - current_price) / current_price)
            if potential > 0.20:
                status = "Infravalorada"
            elif potential < -0.20:
                status = "Sobrevalorada"
            else:
                status = "Precio Justo"
        else:
            status = "N/A"
            potential = None

        return {
            "Ticker": ticker_symbol,
            "Nombre": info.get('shortName', ticker_symbol),
            "Precio Actual": current_price,
            "Valor Justo": fair_value,
            "Potencial": potential,
            "Estado": status,
            "Market Cap": info.get('marketCap'),
            "Div Yield": info.get('dividendYield'),
            "P/E": info.get('trailingPE'),
            "P/B": info.get('priceToBook'),
            "P/S (TTM)": info.get('priceToSalesTrailing12Months'),
            "EV": info.get('enterpriseValue'),
            "Deuda/Eq": info.get('debtToEquity'),
            "Técnico": technical_summary,
            "Modelos": model_details
        }
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

@st.cache_data(ttl=900)
def get_etf_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice') or info.get('navPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None

        high_52w = info.get('fiftyTwoWeekHigh')
        potential = None
        status = "N/A"
        
        if current_price and high_52w and high_52w > 0:
            potential = (high_52w - current_price) / current_price
            if potential > 0.20:
                status = "Oportunidad de Rebote"
            elif potential > 0.05:
                status = "Recuperando"
            elif potential >= 0:
                status = "Cerca de Máximos"
            else:
                status = "En Máximos"

        return {
            "Ticker": ticker_symbol,
            "Nombre": info.get('shortName', ticker_symbol),
            "Precio": current_price,
            "Potencial": potential,
            "Estado": status,
            "Yield": info.get('yield'),
            "Expense Ratio": info.get('annualReportExpenseRatio'),
            "Retorno YTD": info.get('ytdReturn'),
            "Categoría": info.get('category'),
            "Activos": info.get('totalAssets')
        }
    except Exception as e:
        print(f"Error fetching ETF data for {ticker_symbol}: {e}")
        return None

@st.cache_data(ttl=300)
def get_crypto_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not current_price:
            return None
            
        ma50 = info.get('fiftyDayAverage')
        ma200 = info.get('twoHundredDayAverage')
        trend = "Neutro"
        if ma50 and ma200:
            if current_price > ma50 and current_price > ma200:
                trend = "Alcista (Bullish)"
            elif current_price < ma50 and current_price < ma200:
                trend = "Bajista (Bearish)"
        else:
             trend = "N/A"

        high_52w = info.get('fiftyTwoWeekHigh')
        potential = None
        status = "Neutro"
        
        if current_price and high_52w and high_52w > 0:
            potential = (high_52w - current_price) / current_price
            if potential > 0.20:
                status = "Oportunidad de Rebote"
            elif potential > 0.05:
                status = "Recuperando"
            elif potential >= 0:
                status = "Cerca de Máximos"
            else:
                status = "En Máximos"

        return {
            "Ticker": ticker_symbol,
            "Nombre": info.get('shortName', ticker_symbol),
            "Precio": current_price,
            "Potencial": potential,
            "Estado": status,
            "Tendencia": trend,
            "Market Cap": info.get('marketCap'),
            "Volumen 24h": info.get('volume24Hr'),
            "Circulating Supply": info.get('circulatingSupply'),
            "MA 50d": ma50,
            "MA 200d": ma200
        }
    except Exception as e:
        print(f"Error fetching Crypto data for {ticker_symbol}: {e}")
        return None

def fetch_concurrently(tickers, fetch_func, max_workers=10):
    """
    Fetches data for multiple tickers concurrently using a thread pool.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(fetch_func, tickers))
    return [r for r in results if r is not None]
