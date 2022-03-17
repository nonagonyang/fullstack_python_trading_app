from symtable import Symbol
from flask import Flask, request, redirect, render_template,session
from models import db, connect_db, Stock, StockPrice,Strategy,Stock_Strategy
from forms import ApplyStrategyForm
from datetime import date,datetime
from sqlalchemy.sql.expression import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///python_trader_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

connect_db(app)

CURRENT_DATE=date.today().isoformat()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stocks")
def show_stocks():
    filter=request.args.get("filter")
    if filter=="new_closing_highs":
        subquery=db.session.query(func.max(StockPrice.close)).group_by(StockPrice.stock_id).filter(date=='2022-03-14').all()
        stocks=Stock.query.filter(Stock.id.in_(subquery)).all()
    elif filter=="new_closing_lows":
        subquery=db.session.query(func.min(StockPrice.close)).group_by(StockPrice.stock_id).filter_by(date='2022-03-14').all()
        stocks=Stock.query.filter(Stock.id.in_(subquery)).all()
    else:
        stocks=Stock.query.order_by("symbol").all()
    return render_template("stocks.html",stocks=stocks)


@app.route("/stocks/<symbol>",methods=["GET", "POST"])
def stock_details(symbol):
    stock=Stock.query.filter_by(symbol=symbol).first()
    prices=StockPrice.query.filter_by(stock_id=stock.id).all()

    form=ApplyStrategyForm()
    form.strategy_id.choices = [(s.id, s.name) for s in Strategy.query.order_by('name').all()]

    if form.validate_on_submit():
        stock_strategy=Stock_Strategy(stock_id=stock.id, strategy_id=form.strategy_id.data)
        db.session.add(stock_strategy)
        db.session.commit()
        return redirect(f"/strategies")
    return render_template("prices.html",stock=stock,prices=prices, form=form)                                            

@app.route("/strategies")
def show_strategies():
    strategies=Strategy.query.all()
    return render_template("strategies.html",strategies=strategies)



