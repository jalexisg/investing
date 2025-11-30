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
        
if __name__ == '__main__':
    unittest.main()
