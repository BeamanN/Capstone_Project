from config import ALPACA_CONFIG
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BuyHold(Strategy):
    """
    A simple Buy-and-Hold strategy that invests in a set of symbols at the first iteration
    and holds them until the end of the backtest or live trading.
    """

    def initialize(self):
        """Initialize the strategy with parameters."""
        self.sleeptime = "1D"  # Sleep for 1 day between iterations
        self.symbols = ["GOOG", "AAPL", "MSFT"]  # List of symbols to invest in
        self.portfolio_allocation = {symbol: 1 / len(self.symbols) for symbol in self.symbols}  # Equal allocation
        self.first_iteration = True  # Flag to track the first iteration
        logger.info("Strategy initialized with symbols: %s", self.symbols)

    def on_trading_iteration(self):
        """Main trading logic that runs on each iteration."""
        try:
            if self.first_iteration:
                # Invest in each symbol at the first iteration
                for symbol in self.symbols:
                    price = self.get_last_price(symbol)
                    if price is None:
                        logger.error(f"Unable to get price for {symbol}. Skipping.")
                        continue

                    # Calculate the quantity based on portfolio allocation
                    quantity = (self.cash * self.portfolio_allocation[symbol]) // price
                    if quantity > 0:
                        order = self.create_order(symbol, quantity, "buy")
                        self.submit_order(order)
                        logger.info(f"Placed buy order for {quantity} shares of {symbol} at {price}.")
                    else:
                        logger.warning(f"Not enough cash to buy {symbol}.")

                self.first_iteration = False  # Ensure this block runs only once

            # Log portfolio value at each iteration
            portfolio_value = self.get_portfolio_value()
            logger.info(f"Current Portfolio Value: {portfolio_value}")

        except Exception as e:
            logger.error(f"An error occurred during trading iteration: {e}")

    def before_market_closes(self):
        """Actions to perform before the market closes."""
        try:
            logger.info("Market is about to close. No action taken.")
        except Exception as e:
            logger.error(f"An error occurred before market close: {e}")

    def on_error(self, error):
        """Handle any errors that occur during trading."""
        logger.error(f"Error occurred: {error}")


if __name__ == "__main__":
    trade = False  # Set to True for live trading, False for backtesting

    if trade:
        # Live trading with Alpaca
        try:
            broker = Alpaca(ALPACA_CONFIG)
            strategy = BuyHold(broker=broker)
            trader = Trader()
            trader.add_strategy(strategy)
            logger.info("Starting live trading...")
            trader.run_all()
        except Exception as e:
            logger.error(f"An error occurred during live trading: {e}")
    else:
        # Backtesting with Yahoo Finance data
        try:
            start = datetime(2022, 1, 1)
            end = datetime(2022, 12, 31)
            logger.info(f"Starting backtest from {start} to {end}...")
            BuyHold.backtest(
                YahooDataBacktesting,
                start,
                end,
                benchmark_asset="SPY",  # Compare performance to SPY (S&P 500 ETF)
                stats=True,  # Generate performance statistics
                show_plot=True,  # Show a plot of the portfolio value
                buy_trend=True,  # Plot buy signals on the chart
                sell_trend=False,  # No sell signals in Buy-and-Hold
            )
        except Exception as e:
            logger.error(f"An error occurred during backtesting: {e}")