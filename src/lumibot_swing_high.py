from config import ALPACA_CONFIG
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SwingHigh(Strategy):
    data = []  # List to store historical prices
    order_number = 0  # Counter to keep track of the number of orders placed
    entry_price = None  # Variable to store the entry price of the position

    def initialize(self):
        """Initialize the strategy with any required parameters."""
        self.sleeptime = "10S"  # Set the sleep time between trading iterations
        self.symbol = "GOOG"  # Define the trading symbol
        self.quantity = 10  # Define the quantity of shares to trade
        self.stop_loss_percent = 0.5  # Stop loss percentage (0.5%)
        self.take_profit_percent = 1.5  # Take profit percentage (1.5%)
        logger.info("Strategy initialized with symbol %s and quantity %d", self.symbol, self.quantity)

    def on_trading_iteration(self):
        """Main trading logic that runs on each iteration."""
        try:
            # Get the last price for the symbol
            last_price = self.get_last_price(self.symbol)
            self.data.append(last_price)  # Append the last price to the data list

            # Log the current position
            position = self.get_position(self.symbol)
            logger.info(f"Current Position for {self.symbol}: {position}")

            # Check if we have enough data points to make a decision
            if len(self.data) > 3:
                temp = self.data[-3:]  # Get the last three data points

                # Check for a swing high pattern
                if temp[-1] > temp[1] > temp[0]:
                    logger.info(f"Swing High pattern detected for {self.symbol}. Last 3 prices: {temp}")
                    if not self.get_position(self.symbol):  # Check if we don't already have a position
                        # Place a buy order
                        order = self.create_order(self.symbol, quantity=self.quantity, side="buy")
                        self.submit_order(order)
                        self.order_number += 1
                        self.entry_price = temp[-1]  # Set the entry price
                        logger.info(f"Buy order placed for {self.symbol} at {self.entry_price}. Order number: {self.order_number}")

            # Check if we have an open position
            if self.get_position(self.symbol):
                # Calculate stop loss and take profit levels
                stop_loss_price = self.entry_price * (1 - self.stop_loss_percent / 100)
                take_profit_price = self.entry_price * (1 + self.take_profit_percent / 100)

                # Check if the current price has hit the stop loss or take profit levels
                if self.data[-1] <= stop_loss_price or self.data[-1] >= take_profit_price:
                    self.sell_all()  # Sell all positions
                    self.order_number = 0  # Reset the order number
                    self.entry_price = None  # Reset the entry price
                    logger.info(f"Position closed for {self.symbol} at {self.data[-1]}. Order number reset.")

        except Exception as e:
            logger.error(f"An error occurred during trading iteration: {e}")

    def before_market_closes(self):
        """Ensure all positions are closed before the market closes."""
        try:
            if self.get_position(self.symbol):
                self.sell_all()  # Sell all positions
                self.order_number = 0  # Reset the order number
                self.entry_price = None  # Reset the entry price
                logger.info(f"Market closing soon. Position closed for {self.symbol}.")
        except Exception as e:
            logger.error(f"An error occurred before market close: {e}")

    def on_error(self, error):
        """Handle any errors that occur during trading."""
        logger.error(f"Error occurred: {error}")

if __name__ == "__main__":
    try:
        # Initialize the broker and strategy
        broker = Alpaca(ALPACA_CONFIG)
        strategy = SwingHigh(broker=broker)
        trader = Trader()
        trader.add_strategy(strategy)
        logger.info("Starting trader...")
        trader.run_all()  # Run the trader
    except Exception as e:
        logger.error(f"An error occurred while running the trader: {e}")