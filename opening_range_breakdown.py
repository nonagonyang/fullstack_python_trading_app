from models import db, connect_db, Stock, StockPrice,Strategy,Stock_Strategy
from flask_sqlalchemy import SQLAlchemy
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame,TimeFrameUnit
import config
from flask import Flask, request, redirect, render_template,session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///python_trader_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

connect_db(app)

api=tradeapi.REST(config.API_KEY_ID,
                config.SECRET_KEY,
                base_url=config.BASE_URL)

import smtplib, ssl


from datetime import datetime, timedelta
from timezone import is_dst

# Notes: due to account limit, can't retrive minute_bar on the current date.
# Otherwise we can use current_date=datetime.today().isoformat()
yesterday = (datetime.today() - timedelta(days=1)).isoformat()

if is_dst():
    start_minute_bar =f" {yesterday} 09:30:00-05:00"
    end_minute_bar =f" {yesterday}  09:45:00-05:00"
else:
    start_minute_bar =f" {yesterday} 09:30:00-04:00"
    end_minute_bar =f" {yesterday}  09:45:00-04:00"

# checking all the orders, so we don't repeat the same order over and over again.

orders= api.list_orders(status="all", after=yesterday)
existing_orders_symbols=[order.symbol for order  in orders if order.status !="canceled"]


context = ssl.create_default_context()
messages=[]

# openning_range_breakout
strategy=Strategy.query.filter_by(name="openning_range_breakdown").first()
stocks=strategy.stocks
symbols=[stock.symbol for stock in stocks]
# print(symbols)


for symbol in symbols:
    minute_bars=api.get_bars_iter(symbol, TimeFrame(1, TimeFrameUnit.Minute), yesterday, yesterday)
    minute_bars_list=[minute_bar for minute_bar in minute_bars]
    print(f"There are {len(minute_bars_list)} minute_bars in total")
    print(minute_bars_list[0:15])
    opening_range_bars=minute_bars_list[0:15]
    after_opening_range_bars=minute_bars_list[15:]
    opening_range_high=opening_range_bars[0].h
    opening_range_low=opening_range_bars[0].l
    for bar in opening_range_bars:
        if bar.h>opening_range_high:
            opening_range_high=bar.h
        if bar.l<opening_range_low:
            opening_range_low=bar.l
    print (f" {symbol}'s opening high is {opening_range_high}")
    opening_range=opening_range_high - opening_range_low
    print(f" {symbol}'s opening_range is {opening_range}")
    
    for bar in after_opening_range_bars:
        if bar.c < opening_range_low:
            limit_price=bar.c
            messages.append(f"placing order for {symbol} at {limit_price}, closing above {opening_range_high}\n\n")
            # Use Alpaca's submit order function: a bracket order
            if symbol not in existing_orders_symbols:
                api.submit_order(
                    symbol=symbol,
                    qty=1,
                    side='buy',
                    type='limit',
                    time_in_force='day',
                    order_class='bracket',
                    limit_price=limit_price,
                    stop_loss={'stop_price':limit_price-opening_range },
                    take_profit={'limit_price':limit_price+opening_range})
            else:
                print("You have an order for this symbol already") 

        

    # opening_range_high=opening_range_bars["high"].max()
    # opening_range_low=opening_range_bars["low"].min()
    # opening_range=opening_range_high-opening_range_low
    # print(f"opening range high is {opening_range_high}, opening range low is {opening_range_low}, opening_range is {opening_range}")
    # opening_range_bars=filter(lambda minute_bar: minute_bar.t>=start_minute_bar and minute_bar.t<end_minute_bar, minute_bars_list)
    # print(f"There are {len(list(opening_range_bars))} opening range bars")

    # opening_range_mask=(minute_bars_list.index>=start_minute_bar)&(minute_bars_list.index<end_minute_bar)
    # opening_range_bars=minute_bars_list.loc[opening_range_mask]
    # print(opening_range_bars)
        # opening_range_high=opening_range_bars["high"].max()
        # opening_range_low=opening_range_bars["low"].min()
        # opening_range=opening_range_high-opening_range_low

        # after_opening_range_mask=minute_bars.index>=end_minute_bar
        # after_opening_range_bars=minute_bars.loc[after_opening_range_mask]
        # after_opening_range_breakout=after_opening_range_bars[after_opening_range_bars["close"] >opening_range_high ]

        # # check if we have an openning range breakout
        # if not after_opening_range_breakout.empty():

        #     # make sure we won't place this order again
        #     if symbol not in existing_orders_symbols:
        #         limit_price=after_opening_range_breakout.iloc[0]["close"]
        #         messages.append(f"placing order for {symbol} at {limit price}, closing above {opening_range_high}\n\n")

        #         # Use Alpaca's submit order function: a bracket order
        #         api.submit_order(
        #             symbol=symbol,
        #             qty=1,
        #             side='buy',
        #             type='limit',
        #             time_in_force='day',
        #             order_class='bracket',
        #             limit_price=limit_price,
        #             stop_loss={'stop_price':limit_price-opening_range },
        #             take_profit={'limit_price':limit_price+opening_range})
        #     else:
        #         print("You have an order for this symbol already") 





# Email and SMS notifications
# Create a secure SSL context

with smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT, context=context) as server:
    server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    # Send email here
    email_message=f"Subject: Trade Notification\n\n"
    email_message +="\n\n".join(messages)
    server.sendmail(config.EMAIL_ADDRESS,config.EMAIL_ADDRESS)