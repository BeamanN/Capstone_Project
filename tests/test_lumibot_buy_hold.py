import unittest
from unittest.mock import MagicMock, patch
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader

# Import the BuyHold strategy class
from src.lumibot_buy_hold import BuyHold  # Replace `your_module` with the actual module name

class TestBuyHoldStrategy(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        # Mock the Alpaca broker
        self.broker = MagicMock(spec=Alpaca)
        self.strategy = BuyHold(broker=self.broker)
        self.strategy.initialize()

    @patch('src.lumibot_buy_hold.BuyHold.get_last_price')
    @patch('src.lumibot_buy_hold.BuyHold.create_order')
    @patch('src.lumibot_buy_hold.BuyHold.submit_order')
    def test_first_iteration_buy_orders(self, mock_submit_order, mock_create_order, mock_get_last_price):
        """Test that buy orders are placed for all symbols on the first iteration."""
        # Mock the last prices for the symbols
        mock_get_last_price.side_effect = [2800.50, 150.75, 300.25]  # Prices for GOOG, AAPL, MSFT
        self.strategy.cash = 100000  # Set initial cash

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that buy orders were created and submitted for all symbols
        self.assertEqual(mock_create_order.call_count, 3)
        mock_submit_order.assert_called()

    @patch('src.lumibot_buy_hold.BuyHold.get_last_price')
    @patch('src.lumibot_buy_hold.BuyHold.create_order')
    @patch('src.lumibot_buy_hold.BuyHold.submit_order')
    def test_insufficient_cash(self, mock_submit_order, mock_create_order, mock_get_last_price):
        """Test that no orders are placed if there is insufficient cash."""
        # Mock the last prices for the symbols
        mock_get_last_price.side_effect = [2800.50, 150.75, 300.25]  # Prices for GOOG, AAPL, MSFT
        self.strategy.cash = 100  # Set insufficient cash

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that no orders were created
        mock_create_order.assert_not_called()
        mock_submit_order.assert_not_called()

    @patch('src.lumibot_buy_hold.BuyHold.get_portfolio_value')
    @patch('src.lumibot_buy_hold.BuyHold.logger')
    def test_portfolio_value_logging(self, mock_logger, mock_get_portfolio_value):
        """Test that the portfolio value is logged correctly."""
        # Mock the portfolio value
        mock_get_portfolio_value.return_value = 100000

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that the portfolio value was logged
        mock_logger.info.assert_called_with("Current Portfolio Value: 100000")

    @patch('src.lumibot_buy_hold.BuyHold.logger')
    def test_before_market_close(self, mock_logger):
        """Test that the strategy logs a message before market close."""
        # Run the before_market_closes method
        self.strategy.before_market_closes()

        # Verify that the message was logged
        mock_logger.info.assert_called_with("Market is about to close. No action taken.")

    @patch('src.lumibot_buy_hold.BuyHold.get_last_price')
    @patch('src.lumibot_buy_hold.BuyHold.logger')
    def test_error_handling(self, mock_logger, mock_get_last_price):
        """Test that errors during trading iteration are logged."""
        # Simulate an error in get_last_price
        mock_get_last_price.side_effect = Exception("Test error")

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that the error was logged
        mock_logger.error.assert_called_with("An error occurred during trading iteration: Test error")

if __name__ == "__main__":
    unittest.main()