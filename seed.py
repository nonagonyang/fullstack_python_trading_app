from readline import set_completion_display_matches_hook
from app import app
from models import db, Stock,StockPrice,Strategy,Stock_Strategy
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import config
from datetime import datetime

import numpy, tulipy


db.drop_all()
db.create_all()

Stock.query.delete()
StockPrice.query.delete()


#populate the stocks table in database by using alpaca api

api=tradeapi.REST(config.API_KEY_ID,
                config.SECRET_KEY,
                base_url=config.BASE_URL)
active_assets = api.list_assets(status='active')
nasdaq_assets = [a for a in active_assets if a.exchange == 'NASDAQ']

for asset in nasdaq_assets:
    try:
        if asset.tradable:
            stock=Stock(symbol=asset.symbol, name=asset.name, exchange=asset.exchange)
            db.session.add(stock)
    except: 
        pass
db.session.commit()


stocks=Stock.query.all()
symbollist=[stock.symbol for stock in stocks]
stock_dict={}
for stock in stocks:
    stock_dict[stock.symbol]=stock.id

#populate the stockprices table in database by using alpaca api

#loop through the stocks in chunk sizes at a time
chunk_size=200
for i in range(0,len(symbollist),chunk_size):
    symbol_chunk=symbollist[i:i+chunk_size]
    bars=api.get_bars(symbol_chunk,TimeFrame.Day,"2022-01-01","2022-03-15")

    recent_closes=[bar.c for bar in bars]
    if len(recent_closes)>=50:
        sma_20=tulipy.sma(numpy.arrary(recent_closes), period=20)
        rsi_14=tulipy.rsi(numpy.arrary(recent_closes), period=14)
        
    for bar in bars:
        stockprice=StockPrice(stock_id=stock_dict[bar.S],
                            date=bar.t,
                            open=bar.o,
                            high=bar.h,
                            low=bar.l,
                            close=bar.c,
                            volumn=bar.v,
                            sma_20=sma_20,
                            rsi_14=rsi_14)
        db.session.add(stockprice)

db.session.commit()

recent_closes=[bar.c for bar in bars]
if len(recent_closes)>=50:
    sma_20=tulipy.sma(numpy.arrary(recent_closes), period=20)
    rsi_14=tulipy.rsi(numpy.arrary(recent_closes), period=14)





#populate the strategies table in database manually
strategies=["openning_range_breakout","openning_range_breakdown"]
for strategy in strategies:
    strategy=Strategy(name=strategy)
    db.session.add(strategy)
db.session.commit()