import unittest
from unittest.mock import MagicMock, patch
from lumibot.brokers import Alpaca
from lumibot.strategies import Strategy
from lumibot.traders import Trader

# Import the SwingHigh strategy class
from src.lumibot_swing_high import SwingHigh  # Replace `your_module` with the actual module name

class TestSwingHighStrategy(unittest.TestCase):

    def setUp(self):
        """Set up the test environment."""
        # Mock the Alpaca broker
        self.broker = MagicMock(spec=Alpaca)
        self.strategy = SwingHigh(broker=self.broker)
        self.strategy.initialize()

    @patch('src.lumibot_swing_high.SwingHigh.get_last_price')
    @patch('src.lumibot_swing_high.SwingHigh.get_position')
    @patch('src.lumibot_swing_high.SwingHigh.create_order')
    def test_swing_high_pattern_detection(self, mock_create_order, mock_get_position, mock_get_last_price):
        """Test that a buy order is placed when a swing high pattern is detected."""
        # Mock the last prices to simulate a swing high pattern
        mock_get_last_price.side_effect = [100, 105, 110]  # Last three prices
        mock_get_position.return_value = None  # No existing position

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that a buy order was created
        mock_create_order.assert_called_once_with(self.strategy.symbol, quantity=self.strategy.quantity, side="buy")

    @patch('src.lumibot_swing_high.SwingHigh.get_last_price')
    @patch('src.lumibot_swing_high.SwingHigh.get_position')
    @patch('src.lumibot_swing_high.SwingHigh.sell_all')
    def test_stop_loss_trigger(self, mock_sell_all, mock_get_position, mock_get_last_price):
        """Test that the position is sold when the stop loss is triggered."""
        # Set up the entry price
        self.strategy.entry_price = 100

        # Mock the last price to trigger the stop loss
        mock_get_last_price.return_value = 99.5  # Below stop loss level (100 * 0.995)
        mock_get_position.return_value = MagicMock()  # Simulate an existing position

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that sell_all was called
        mock_sell_all.assert_called_once()

    @patch('src.lumibot_swing_high.SwingHigh.get_last_price')
    @patch('src.lumibot_swing_high.SwingHigh.get_position')
    @patch('src.lumibot_swing_high.SwingHigh.sell_all')
    def test_take_profit_trigger(self, mock_sell_all, mock_get_position, mock_get_last_price):
        """Test that the position is sold when the take profit is triggered."""
        # Set up the entry price
        self.strategy.entry_price = 100

        # Mock the last price to trigger the take profit
        mock_get_last_price.return_value = 101.5  # Above take profit level (100 * 1.015)
        mock_get_position.return_value = MagicMock()  # Simulate an existing position

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that sell_all was called
        mock_sell_all.assert_called_once()

    @patch('src.lumibot_swing_high.SwingHigh.get_position')
    @patch('src.lumibot_swing_high.SwingHigh.sell_all')
    def test_before_market_close(self, mock_sell_all, mock_get_position):
        """Test that all positions are sold before the market closes."""
        # Simulate an existing position
        mock_get_position.return_value = MagicMock()

        # Run the before_market_closes method
        self.strategy.before_market_closes()

        # Verify that sell_all was called
        mock_sell_all.assert_called_once()

    @patch('src.lumibot_swing_high.SwingHigh.get_last_price')
    @patch('src.lumibot_swing_high.SwingHigh.get_position')
    @patch('src.lumibot_swing_high.SwingHigh.create_order')
    def test_no_swing_high_pattern(self, mock_create_order, mock_get_position, mock_get_last_price):
        """Test that no orders are placed when no swing high pattern is detected."""
        # Mock the last prices to simulate no swing high pattern
        mock_get_last_price.side_effect = [100, 95, 90]  # Last three prices
        mock_get_position.return_value = None  # No existing position

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that no orders were created
        mock_create_order.assert_not_called()

    @patch('src.lumibot_swing_high.SwingHigh.get_last_price')
    @patch('src.lumibot_swing_high.SwingHigh.get_position')
    @patch('src.lumibot_swing_high.SwingHigh.logger')
    def test_error_handling(self, mock_logger, mock_get_position, mock_get_last_price):
        """Test that errors during trading iteration are logged."""
        # Simulate an error in get_last_price
        mock_get_last_price.side_effect = Exception("Test error")

        # Run the trading iteration
        self.strategy.on_trading_iteration()

        # Verify that the error was logged
        mock_logger.error.assert_called_with("An error occurred during trading iteration: Test error")

if __name__ == "__main__":
    unittest.main()