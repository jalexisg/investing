# Debug Utils

> **Description**: A collection of standalone Python scripts for debugging market data, valuation models, and ticker information.

## Scripts

### `scripts/debug_msft.py`
Runs a full debugging suite for Microsoft (MSFT).
- Checks `yfinance` connectivity.
- Retrieves current price, PE ratios, and EPS.
- Calculates fair value using historical data.
- **Usage**: `python skills/debug_utils/scripts/debug_msft.py`

### `scripts/debug_targets.py`
Checks analyst target prices for tickers.
- **Usage**: `python skills/debug_utils/scripts/debug_targets.py`

### `scripts/debug_valuation.py`
Debugs the valuation logic for a specific ticker.
- **Usage**: `python skills/debug_utils/scripts/debug_valuation.py`

### `scripts/debug_yf.py`
Simple connectivity test for Yahoo Finance API.
- **Usage**: `python skills/debug_utils/scripts/debug_yf.py`

## Instructions
Use these scripts when you need to verify if the data source (`yfinance`) is returning expected values or if the calculation logic in the main app is producing weird results.
