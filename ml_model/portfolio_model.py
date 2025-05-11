from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Portfolio model representing a stock holding
class PortfolioModel(db.Model):
    __tablename__ = 'portfolio'  # Explicit table name

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    average_buy_price = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Auto timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    note = db.Column(db.String(255), nullable=True)  # Optional note column

    def __repr__(self):
        return f"<PortfolioModel {self.symbol} - {self.quantity} shares at ₹{self.average_buy_price}>"
