from utils.ml_model import PortfolioModel, db  # Corrected import path for modularity
import yfinance as yf
import logging
# portfolio_manager.py
from ml_model.portfolio_model import db, PortfolioModel

# Setup basic logging
logging.basicConfig(level=logging.INFO)

class Portfolio:
    def __init__(self):
        pass  # All operations are database-driven

    def add_stock(self, symbol, quantity, buy_price):
        """
        Add or update a stock in the portfolio.

        Args:
            symbol (str): Stock ticker symbol.
            quantity (float): Number of shares to add.
            buy_price (float): Price at which the stock was bought.
        """
        if not symbol or quantity <= 0 or buy_price <= 0:
            logging.warning("Invalid input for adding stock.")
            return

        symbol = symbol.upper()
        stock = PortfolioModel.query.filter_by(symbol=symbol).first()

        if stock:
            # Option: Keep simple or use average buy price
            total_quantity = stock.quantity + quantity
            stock.buy_price = (stock.quantity * stock.buy_price + quantity * buy_price) / total_quantity
            stock.quantity = total_quantity
            logging.info(f"Updated {symbol} in portfolio.")
        else:
            new_stock = PortfolioModel(symbol=symbol, quantity=quantity, buy_price=buy_price)
            db.session.add(new_stock)
            logging.info(f"Added new stock {symbol} to portfolio.")

        db.session.commit()

    def remove_stock(self, symbol):
        """
        Remove a stock from the portfolio.

        Args:
            symbol (str): Stock ticker symbol.
        """
        symbol = symbol.upper()
        stock = PortfolioModel.query.filter_by(symbol=symbol).first()

        if stock:
            db.session.delete(stock)
            db.session.commit()
            logging.info(f"Removed {symbol} from portfolio.")
        else:
            logging.warning(f"{symbol} not found in portfolio.")

    def get_portfolio_summary(self):
        """
        Generate a detailed portfolio summary with profit/loss and valuation.

        Returns:
            summary (list): Per-stock data.
            total_investment (float)
            total_value (float)
            total_profit_loss (float)
        """
        summary = []
        total_investment = 0
        total_value = 0
        total_profit_loss = 0

        stocks = PortfolioModel.query.all()

        for stock in stocks:
            try:
                ticker = yf.Ticker(stock.symbol)
                current_price = ticker.info.get("currentPrice", 0)

                if current_price == 0:
                    logging.warning(f"Could not fetch price for {stock.symbol}")

                quantity = stock.quantity
                buy_price = stock.buy_price

                investment = quantity * buy_price
                current_value = quantity * current_price
                profit_loss = current_value - investment

                total_investment += investment
                total_value += current_value
                total_profit_loss += profit_loss

                summary.append({
                    "symbol": stock.symbol,
                    "quantity": quantity,
                    "buy_price": buy_price,
                    "current_price": current_price,
                    "current_value": current_value,
                    "profit_loss": profit_loss
                })

            except Exception as e:
                logging.error(f"Error fetching data for {stock.symbol}: {e}")
                continue

        return summary, total_investment, total_value, total_profit_loss
