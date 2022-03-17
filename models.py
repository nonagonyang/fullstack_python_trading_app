"""Models for Python-Trader app."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class Stock(db.Model):
    """Stock"""
    __tablename__="stocks"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol=db.Column(db.Text, nullable=False)
    name=db.Column(db.Text, nullable=False)
    exchange=db.Column(db.Text, nullable=False)
    prices=db.relationship("StockPrice",backref="stock")

class StockPrice(db.Model):
    """StockPrice"""
    __tablename__="stockprices"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    stock_id=db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date=db.Column(db.DateTime, nullable=False)
    open=db.Column(db.Float, nullable=False)
    high=db.Column(db.Float, nullable=False)
    low=db.Column(db.Float, nullable=False)
    close=db.Column(db.Float, nullable=False)
    volumn=db.Column(db.Integer,nullable=False)
    # sma_20=db.Column(db.Float, nullable=True)
    # rsi_14=db.Column(db.Float, nullable=True)

class Strategy(db.Model):
    """Strategy"""
    __tablename__="strategies"
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name=db.Column(db.Text, nullable=False)
    stocks=db.relationship("Stock",secondary="stocks_strategies",backref="strategies")

class Stock_Strategy(db.Model):
    """Stock_Strategy"""
    __tablename__="stocks_strategies"
    stock_id=db.Column(db.Integer, db.ForeignKey('stocks.id'),primary_key=True, nullable=False)
    strategy_id=db.Column(db.Integer, db.ForeignKey('strategies.id'), primary_key=True,nullable=False)

