import os
import sys
from unittest.mock import MagicMock
import unittest
from unittest.mock import patch
import pandas as pd

# Add parent directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Mock Streamlit before importing app ---
mock_st = MagicMock()

# Mock cache_data to be a pass-through decorator
def cache_data_mock(**kwargs):
    def decorator(func):
        return func
    return decorator

mock_st.cache_data = cache_data_mock
mock_st.set_page_config = MagicMock()
mock_st.markdown = MagicMock()

# Mock SessionState to support both attribute and item access
class MockSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

mock_st.session_state = MockSessionState()

# Mock dynamic elements
def columns_mock(spec):
    if isinstance(spec, int):
        return [MagicMock() for _ in range(spec)]
    elif isinstance(spec, (list, tuple)):
        return [MagicMock() for _ in range(len(spec))]
    return [MagicMock()]

mock_st.columns.side_effect = columns_mock

def tabs_mock(spec):
    return [MagicMock() for _ in range(len(spec))]

mock_st.tabs.side_effect = tabs_mock

# Prevent interactive elements from triggering logic during import
mock_st.button.return_value = False
mock_st.selectbox.return_value = ""
mock_st.multiselect.return_value = []

# Mock column_config classes
mock_st.column_config.TextColumn = MagicMock()
mock_st.column_config.NumberColumn = MagicMock()
mock_st.column_config.ProgressColumn = MagicMock()

sys.modules["streamlit"] = mock_st

# --- Import app ---
import app

class TestApp(unittest.TestCase):

    def test_format_large_number(self):
        self.assertEqual(app.format_large_number(1_500_000_000_000), "1.5 T")
        self.assertEqual(app.format_large_number(2_500_000_000), "2.5 B")
        self.assertEqual(app.format_large_number(3_500_000), "3.5 M")
        self.assertEqual(app.format_large_number(100), "100.00")
        self.assertEqual(app.format_large_number(None), "-")

    @patch('app.yf.Ticker')
    def test_get_historical_pe(self, mock_ticker):
        # Setup mock
        mock_instance = mock_ticker.return_value
        
        # Mock financials (EPS)
        data = {
            pd.Timestamp('2023-01-01'): [5.0], 
            pd.Timestamp('2022-01-01'): [4.0]
        }
        df_fin = pd.DataFrame(data, index=['Basic EPS'])
        mock_instance.financials = df_fin
        
        # Mock history (Price)
        dates = pd.to_datetime(['2022-01-01', '2023-01-01'])
        history_data = {'Close': [80.0, 100.0]}
        df_hist = pd.DataFrame(history_data, index=dates)
        mock_instance.history.return_value = df_hist
        
        # Call function
        avg_pe, method = app.get_historical_pe("TEST")
        
        self.assertEqual(avg_pe, 20.0)
        self.assertEqual(method, "5y Historical Avg")

    @patch('app.yf.Ticker')
    def test_get_stock_data_valid(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        
        # Mock info
        mock_instance.info = {
            'currentPrice': 150.0,
            'shortName': 'Test Corp',
            'trailingEps': 5.0,
            'trailingPE': 30.0,
            'forwardPE': 25.0,
            'pegRatio': 1.5,
            'marketCap': 1000000,
            'dividendYield': 0.02,
            'priceToBook': 5.0,
            'priceToSalesTrailing12Months': 3.0,
            'enterpriseValue': 1100000,
            'debtToEquity': 0.5,
            'targetMeanPrice': 160.0 
        }
        
        # Setup for get_historical_pe inside get_stock_data
        data = {pd.Timestamp('2023-01-01'): [5.0]}
        mock_instance.financials = pd.DataFrame(data, index=['Basic EPS'])
        mock_instance.history.return_value = pd.DataFrame({'Close': [100.0]}, index=[pd.Timestamp('2023-01-01')])

        result = app.get_stock_data("TEST")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['Ticker'], "TEST")
        self.assertEqual(result['Precio Actual'], 150.0)
        self.assertIsNotNone(result['Valor Justo'])

    def test_load_tickers_migration(self):
        # Test 1: File stores a list (legacy)
        with patch("builtins.open", unittest.mock.mock_open(read_data='["AAPL", "TSLA"]')):
            with patch("os.path.exists", return_value=True):
                tickers = app.load_tickers()
                self.assertIsInstance(tickers, dict)
                self.assertEqual(tickers["stocks"], ["AAPL", "TSLA"])
                self.assertEqual(tickers["etfs"], [])
                self.assertEqual(tickers["crypto"], [])

        # Test 2: File stores a dict (new format)
        mock_json = '{"stocks": ["MSFT"], "etfs": ["VOO"], "crypto": ["BTC-USD"]}'
        with patch("builtins.open", unittest.mock.mock_open(read_data=mock_json)):
            with patch("os.path.exists", return_value=True):
                tickers = app.load_tickers()
                self.assertIsInstance(tickers, dict)
                self.assertEqual(tickers["stocks"], ["MSFT"])
                self.assertEqual(tickers["etfs"], ["VOO"])
                self.assertEqual(tickers["crypto"], ["BTC-USD"])

    @patch('app.yf.Ticker')
    def test_get_etf_data(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        mock_instance.info = {
            'currentPrice': 350.0,
            'shortName': 'Vanguard S&P 500',
            'yield': 0.015,
            'annualReportExpenseRatio': 0.0003,
            'ytdReturn': 0.10,
            'category': 'Large Blend',
            'totalAssets': 1000000000,
            'fiftyTwoWeekHigh': 400.0  # Added for Potential calc
        }
        
        result = app.get_etf_data("VOO")
        self.assertIsNotNone(result)
        self.assertEqual(result['Ticker'], "VOO")
        self.assertEqual(result['Yield'], 0.015)
        self.assertIsNotNone(result['Potencial'])
        self.assertIsNotNone(result['Estado'])
        self.assertEqual(result['Expense Ratio'], 0.0003)

    @patch('app.yf.Ticker')
    def test_get_crypto_data(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        mock_instance.info = {
            'currentPrice': 50000.0,
            'shortName': 'Bitcoin',
            'marketCap': 1000000000000,
            'volume24Hr': 30000000000,
            'circulatingSupply': 19000000,
            'volume24Hr': 30000000000,
            'circulatingSupply': 19000000,
            'fiftyDayAverage': 45000.0,
            'twoHundredDayAverage': 40000.0,
            'fiftyTwoWeekHigh': 60000.0 # Added for Potential calc
        }
        
        result = app.get_crypto_data("BTC-USD")
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['Ticker'], "BTC-USD")
        self.assertIsNotNone(result['Potencial'])
        self.assertIsNotNone(result['Estado'])
        self.assertIsNotNone(result['Tendencia'])
        


    def test_render_functions(self):
        # Create dummy dataframes
        df_stocks = pd.DataFrame([{
            'Ticker': 'AAPL', 'Precio Actual': 150.0, 'Valor Justo': 160.0,
            'Potencial': 0.1, 'Estado': 'Infravalorada', 'Market Cap': 1e12,
            'Div Yield': 0.01, 'P/E': 25.0, 'P/B': 10.0, 'P/S (TTM)': 5.0,
            'EV': 1.1e12, 'Deuda/Eq': 0.5, 'Modelos': 'Details'
        }])
        
        df_etfs = pd.DataFrame([{
            'Ticker': 'VOO', 'Nombre': 'Vanguard S&P 500', 'Precio': 400.0,
            'Potencial': 0.05, 'Estado': 'Cerca de Máximos', 'Yield': 0.015,
            'Expense Ratio': 0.0003, 'Retorno YTD': 0.1, 
            'Categoría': 'Large Blend', 'Activos': 1e9
        }])
        
        df_crypto = pd.DataFrame([{
            'Ticker': 'BTC-USD', 'Nombre': 'Bitcoin', 'Precio': 50000.0,
            'Potencial': 0.2, 'Estado': 'Oportunidad de Rebote', 'Tendencia': 'Alcista',
            'Market Cap': 1e12, 'Volumen 24h': 1e9, 
            'MA 50d': 45000.0, 'MA 200d': 40000.0
        }])

        # Call render functions (should not raise error)
        try:
            app.render_dataframe(df_stocks)
            app.render_etf_dataframe(df_etfs)
            app.render_crypto_dataframe(df_crypto)
        except Exception as e:
            self.fail(f"Render functions raised exception: {e}")

    def test_main_execution(self):
        # Setup session state for main
        mock_st.session_state.tickers = {
            "stocks": ["AAPL"], 
            "etfs": [], 
            "crypto": []
        }
        
        # Mock specific interactions to control flow
        # Tab selection: default is first tab (stocks)
        # Search box return empty to skip add logic
        mock_st.text_input.return_value = "" 
        
        # Run main
        try:
            app.main()
        except Exception as e:
             self.fail(f"Main execution raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
