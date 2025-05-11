from flask import Flask, render_template, request, redirect, flash
from ml_model.portfolio_model import db, PortfolioModel
import yfinance as yf
from utils.news_fetcher import fetch_news
from utils.sentiment_analyzer import get_sentiment
from utils.ml_model import train_predict_stock
import os

# Create the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

# Configure SQLite Database using the absolute path to avoid path issues
base_dir = os.path.abspath(os.path.dirname(__file__))  # Get the base directory of the app
db_path = os.path.join(base_dir, 'instance', 'portfolio.db')  # Path to the SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)  # Initialize db through the app

# Portfolio Model
class PortfolioModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Portfolio {self.symbol}>"

# Initialize DB
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/news', methods=['POST'])
def news():
    query = request.form.get('stock', '').strip().upper()
    if not query:
        flash("Please enter a valid stock symbol.")
        return redirect('/')

    try:
        headlines = fetch_news(query)
        analyzed = [(headline, get_sentiment(headline)) for headline in headlines]

        # Count sentiment types
        sentiment_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
        for _, sentiment in analyzed:
            sentiment_counts[sentiment] += 1

        # Decision logic
        if sentiment_counts["BUY"] > sentiment_counts["SELL"] and sentiment_counts["BUY"] > sentiment_counts["HOLD"]:
            final_decision = "BUY"
        elif sentiment_counts["SELL"] > sentiment_counts["BUY"] and sentiment_counts["SELL"] > sentiment_counts["HOLD"]:
            final_decision = "SELL"
        else:
            final_decision = "HOLD"

        return render_template('news.html', analyzed=analyzed, query=query, decision=final_decision)

    except Exception as e:
        flash(f"Error fetching news: {str(e)}")
        return redirect('/')

@app.route('/portfolio')
def portfolio_page():
    """Display portfolio summary and analysis."""
    portfolio_data = PortfolioModel.query.all()
    summary = []
    total_investment = total_value = total_profit_loss = 0

    if not portfolio_data:
        flash("Your portfolio is empty.")
        
    for stock in portfolio_data:
        try:
            ticker = yf.Ticker(stock.symbol)
            history = ticker.history(period='1d')
            current_price = history['Close'].iloc[0] if not history.empty else 0
        except Exception:
            current_price = 0

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
            "current_price": round(current_price, 2),
            "current_value": round(current_value, 2),
            "profit_loss": round(profit_loss, 2)
        })

    return render_template('portfolio.html',
                           summary=summary,
                           invested=round(total_investment, 2),
                           value=round(total_value, 2),
                           pnl=round(total_profit_loss, 2))

@app.route('/add_stock', methods=['POST'])
def add_to_portfolio():
    """Add or update a stock entry in the portfolio."""
    symbol = request.form.get('symbol', '').strip().upper()
    try:
        quantity = float(request.form['quantity'])
        buy_price = float(request.form['buy_price'])

        stock = PortfolioModel.query.filter_by(symbol=symbol).first()
        if stock:
            # Optional: use average buy price instead of replacing
            total_quantity = stock.quantity + quantity
            new_avg_price = ((stock.quantity * stock.buy_price) + (quantity * buy_price)) / total_quantity
            stock.quantity = total_quantity
            stock.buy_price = new_avg_price
        else:
            new_stock = PortfolioModel(symbol=symbol, quantity=quantity, buy_price=buy_price)
            db.session.add(new_stock)

        db.session.commit()
        flash(f"{symbol} added/updated in portfolio.")
    except Exception as e:
        flash(f"Error adding stock: {str(e)}")

    return redirect('/portfolio')

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    """Remove a stock from the portfolio."""
    symbol = request.form.get('symbol', '').strip().upper()
    stock = PortfolioModel.query.filter_by(symbol=symbol).first()
    if stock:
        db.session.delete(stock)
        db.session.commit()
        flash(f"{symbol} removed from portfolio.")
    else:
        flash(f"Stock {symbol} not found.")

    return redirect('/portfolio')

@app.route('/forecast', methods=['POST'])
def forecast():
    """Generate and display stock forecast."""
    symbol = request.form.get('symbol', '').strip().upper()
    try:
        predicted_prices, forecast_image = train_predict_stock(symbol)
        
        # Prepare predicted prices with day labels
        predicted_with_days = [f"Day {i+1} - ₹{price:.2f}" for i, price in enumerate(predicted_prices)]

        return render_template('forecast.html', symbol=symbol,
                               predicted_prices=predicted_with_days,
                               forecast_image=forecast_image)
    except ValueError as e:
        flash(f"Error: {str(e)}")
        return redirect('/')
    
@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)
