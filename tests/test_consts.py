import unittest
from consts import get_ticker_from_string

class TestConsts(unittest.TestCase):
    def test_get_ticker_from_string(self):
        # Test standard format
        self.assertEqual(get_ticker_from_string("Apple Inc. (AAPL)"), "AAPL")
        self.assertEqual(get_ticker_from_string("Bitcoin (BTC-USD)"), "BTC-USD")
        
        # Test edge cases
        self.assertEqual(get_ticker_from_string("AAPL"), "AAPL")
        self.assertEqual(get_ticker_from_string("Company (With) Parentheses (TICK)"), "TICK")
        self.assertEqual(get_ticker_from_string("Invalid Format"), "Invalid Format")

if __name__ == '__main__':
    unittest.main()
