from config import ALPACA_CONFIG
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader
import logging
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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
        self.window_size = 10  # Window size for moving averages
        self.model = None  # Machine learning model
        logger.info("Strategy initialized with symbol %s and quantity %d", self.symbol, self.quantity)

    def fetch_historical_data(self, symbol, days=30):
        """Fetch historical price data using Alpaca's API."""
        try:
            historical_data = self.get_historical_prices(symbol, days=days)
            if historical_data:
                df = historical_data.df  # Convert to Pandas DataFrame
                return df
            else:
                logger.error(f"No historical data found for {symbol}")
                return None
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def calculate_indicators(self, df):
        """Calculate technical indicators using Pandas and NumPy."""
        if df is not None:
            # Calculate moving averages
            df['SMA'] = df['close'].rolling(window=self.window_size).mean()
            df['EMA'] = df['close'].ewm(span=self.window_size, adjust=False).mean()

            # Calculate price change percentage
            df['Price_Change'] = df['close'].pct_change()

            # Drop NaN values
            df.dropna(inplace=True)
            return df
        return None

    def train_model(self, df):
        """Train a simple machine learning model using Scikit-learn."""
        if df is not None:
            # Define features and target
            df['Target'] = np.where(df['Price_Change'] > 0, 1, 0)  # 1 if price increases, 0 otherwise
            features = ['SMA', 'EMA', 'Price_Change']
            X = df[features]
            y = df['Target']

            # Split data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Train a logistic regression model
            model = LogisticRegression()
            model.fit(X_train, y_train)

            # Evaluate the model
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Model trained with accuracy: {accuracy:.2f}")

            return model
        return None

    def on_trading_iteration(self):
        """Main trading logic that runs on each iteration."""
        try:
            # Fetch historical data
            df = self.fetch_historical_data(self.symbol, days=30)
            if df is not None:
                # Calculate technical indicators
                df = self.calculate_indicators(df)

                # Train the model if not already trained
                if self.model is None:
                    self.model = self.train_model(df)

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