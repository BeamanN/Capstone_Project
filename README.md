# Trading Strategy Project

This project implements and backtests trading strategies using the Lumibot framework. It includes a **Buy-and-Hold** strategy and a **Swing High** strategy, with support for both live trading (via Alpaca) and backtesting (using Yahoo Finance data).


---

## Project Overview

This project is designed to:
- Implement trading strategies using the Lumibot framework.
- Support backtesting with historical data (Yahoo Finance).
- Enable live trading via the Alpaca API (paper trading or live trading).
- Provide a modular and scalable structure for adding new strategies.

---

## Strategies

### Buy-and-Hold
A simple strategy that buys a set of symbols (e.g., "GOOG", "AAPL", "MSFT") at the first iteration and holds them until the end of the backtest or live trading session.

### Swing High
A momentum-based strategy that identifies swing high patterns in price data and places buy orders when the pattern is detected. It also includes stop-loss and take-profit mechanisms.
