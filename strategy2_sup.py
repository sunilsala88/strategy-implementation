#super trend and ema strategy
#closing greater than daily ema
#super positive in hourly

import pandas as pd
import datetime 
import time
from ib_insync import *
import pandas as pd
import pandas_ta as ta

import logging
logging.basicConfig(level=logging.INFO, filename=f'orb_{datetime.date.today()}',filemode='w',format="%(asctime)s - %(message)s")

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=77)

account_no='DU8663688'
ord_validity='DAY'
quantity_=1
#start time
start_hour,start_min=19,1
#end time
end_hour,end_min=19,55

list_of_tickers=['MMM', 'AXP'] 
                #  'AMGN', 'AMZN', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'KO', 'DIS', 'DOW', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT', 'NKE', 'PG', 'CRM', 'TRV', 'UNH', 'VZ', 'V', 'WMT']


contract_object={}
for ticker in list_of_tickers:
    c=ib.qualifyContracts(Stock(ticker,'SMART', 'USD'))[0]
    print(c)
    contract_object[ticker]=c
print(contract_object)


def close_ticker_postion(name):
    pos=ib.positions(account=account_no)
    if pos:
        df2=util.df(pos)
        df2['ticker_name']=[cont.symbol for cont in df2['contract']]
        cont=contract_object[name]
        quant=df2[df2['ticker_name']==name].position.iloc[0]
        print(cont)
        print(quant)
        if quant>0:
            #sell
            # ord=MarketOrder(action='SELL',totalQuantity=quant)
            ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action='SELL',account=account_no,tif=ord_validity)
            ib.placeOrder(cont,ord)
            logging.info('Closing position'+'SELL'+name)
        elif quant<0:
            #buy
            # ord=MarketOrder(action='BUY',totalQuantity=quant)
            ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action='BUY',account=account_no,tif=ord_validity)
            ib.placeOrder(cont,ord)
            logging.info('Closing position'+'BUY'+name)




def close_ticker_open_orders(ticker):
    ord=ib.openTrades()
    df1=util.df(ord)
    print(df1)
    if df1:
        print(df1.columns)
        df1['ticker_name']=[cont.symbol for cont in df1['contract']]
        order_object=df1[df1['ticker_name']==ticker].order.iloc[0]
        print(order_object)
        ib.cancelOrder(order_object)
        logging.info('Canceled current order')




def get_historical_data(ticker_contract,bar_size,duration):
    logging.info('fetching historical data')
    bars = ib.reqHistoricalData(
    ticker_contract, endDateTime='', durationStr=duration,
    barSizeSetting=bar_size, whatToShow='MIDPOINT', useRTH=True,formatDate=1)
    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)
    logging.info('calculated indicators')
    df['ema']=ta.ema(df.close, length=20)
    df['super']=ta.supertrend(df.high,df.low,df.close,length=10)['SUPERTd_10_3.0']
    df['atr']=ta.atr(df.high, df.low, df.close, length=14)
    return df

def get_level(hist_df):
    ct=datetime.datetime.now()
    start_range=datetime.datetime(ct.year, ct.month, ct.day-1, 9, 0)
    end_range=datetime.datetime(ct.year, ct.month, ct.day-1, 10, 0)
    
    print(hist_df)
    hist_df['date']=hist_df['date'].dt.tz_localize(None)
    hist_df.set_index('date',inplace=True)
    print(hist_df)
    print(start_range, end_range)


    hist_df=hist_df[start_range:end_range]
    print(hist_df)
    high_level=hist_df.high.max()
    low_level=hist_df.low.min()
    return high_level,low_level

# hl,ll=get_level('BTC')
# print(hl,ll)


def trade_sell_stocks(stock_name,atr_stop): #closing_price, quantitys=1  ????
    #market order
    global current_balance
    #market order
    contract = contract_object[stock_name]
    # ord=MarketOrder(action='SELL',totalQuantity=1,AccountValue=account_no)
    ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action='SELL',account=account_no,tif=ord_validity)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    logging.info(trade)
    logging.info('Placed market sell order')

    #stop order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.action = 'BUY'
    order.orderType = "STP"
    order.totalQuantity = quantity_
    order.auxPrice = int(atr_stop)
    order.tif = ord_validity
    order.account=account_no

    trade=ib.placeOrder(contract,order)
    ib.sleep(1)
    logging.info(trade)
    logging.info("placed stop order")
    



def trade_buy_stocks(stock_name,atr_stop):

    global current_balance
    #market order
    contract = contract_object[stock_name]
    # ord=MarketOrder(action='BUY',totalQuantity=1)
    ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action='BUY',account=account_no,tif=ord_validity)
    trade=ib.placeOrder(contract,ord)
    ib.sleep(1)
    logging.info(trade)
    logging.info('Placed market buy order')


    #stop order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.action = 'SELL'
    order.orderType = "STP"
    order.totalQuantity = quantity_
    order.auxPrice = int(atr_stop)
    order.tif = ord_validity
    order.account=account_no

    trade=ib.placeOrder(contract,order)
    ib.sleep(1)
    logging.info(trade)
    logging.info("placed stop order")


def strategy(hist_df_hourly,hist_df_daily,ticker):
    logging.info('inside strategy')
    print(ticker)
    print(hist_df_hourly)
    print(hist_df_daily)
    hourly_closing_price=hist_df_hourly.close.iloc[-1]
    buy_condition=hist_df_hourly['super'].iloc[-1]>0 and hist_df_daily['ema'].iloc[-1]<hist_df_hourly['close'].iloc[-1]
    # buy_condition=True
    sell_condition=hist_df_hourly['super'].iloc[-1]<0 and hist_df_daily['ema'].iloc[-1]>hist_df_hourly['close'].iloc[-1]
    # sell_condition=True
    current_balance=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))
    atr_value=hist_df_daily['atr'].iloc[-1]
    print(atr_value)
    logging.inof(atr_value)
    if current_balance>hist_df_hourly.close.iloc[-1]:
        if buy_condition:
            logging.info('buy condiiton satisfied')
            trade_buy_stocks(ticker,hourly_closing_price-atr_value)
        elif sell_condition:
            logging.info('sell condition satisfied')
            trade_sell_stocks(ticker,hourly_closing_price+atr_value)
        else :
            logging.info('no condition satisfied')
    else:
        logging.info('we dont have enough money')
        logging.info('current balance is',current_balance,'stock price is ',hist_df_hourly['close'].iloc[-1])


def main_strategy_code():

    print("inside main strategy")
    pos=ib.positions(account=account_no)
    print(pos)
    if len(pos)==0:
        pos_df=pd.DataFrame([])
    else:
        pos_df=util.df(pos)
        pos_df['name']=[cont.symbol for cont in pos_df['contract']]
        pos_df=pos_df[pos_df['position']!=0]
    print(pos_df)
    ord=ib.reqAllOpenOrders()
    if len(ord)==0:
        ord_df=pd.DataFrame([])
    else:
        ord_df=util.df(ord)
        ord_df['name']=[cont.symbol for cont in ord_df['contract']]
    print(ord_df)
    logging.info('Fetched order_df and position_df')

    for ticker in list_of_tickers:
        logging.info(ticker)
        print('ticker name is',ticker,'################')
        ticker_contract=contract_object[ticker]
        hist_df_hourly=get_historical_data(ticker_contract,'1 hour','10 D')
        hist_df_daily=get_historical_data(ticker_contract,'1 day','50 D')
        print(hist_df_hourly)
        print(hist_df_daily)
       
       


        print(hist_df_hourly.close.iloc[-1])
        capital=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))
        print(capital)
        quantity=int((capital/10)/hist_df_hourly.close.iloc[-1])  
        print(quantity)
        logging.info('Checking condition')

        if quantity==0:
            logging.info('we dont have enough money so we cannot trade')
            continue

        if pos_df.empty:
            print('we dont have any position')
            logging.info('we dont have any position')
            strategy(hist_df_hourly,hist_df_daily,ticker)


        elif len(pos_df)!=0 and ticker not in pos_df['name'].tolist():
            logging.info('we have some position but current ticker is not in position')
            print('we have some position but current ticker is not in position')
            strategy(hist_df_hourly,hist_df_daily,ticker)

        elif len(pos_df)!=0 and ticker in pos_df["name"].tolist():
            logging.info('we have some position and current ticker is in position')
            print('we have some position and current ticker is in position')
            
            if pos_df[pos_df["name"]==ticker]["position"].values[0] == 0:
                logging.info('we have current ticker in position but quantity is 0')
                print('we have current ticker in position but quantity is 0')
                strategy(hist_df_hourly,hist_df_daily,ticker)

            elif pos_df[pos_df["name"]==ticker]["position"].values[0] > 0  :
                logging.info('we have current ticker in position and is long')
                print('we have current ticker in position and is long')
                sell_condition=hist_df_hourly['super'].iloc[-1]<0 and hist_df_daily['ema'].iloc[-1]>hist_df_hourly['close'].iloc[-1]
                # sell_condition=True
                # current_balance=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))
                # if current_balance>hist_df.close.iloc[-1]:
                if sell_condition:
                            hourly_closing_price=hist_df_hourly['close'].iloc[0]
                            atr_value=hist_df_daily['atr'].iloc[-1]
                            print('sell condition satisfied')
                            logging.info('sell condition satisfied')
                            close_ticker_open_orders(ticker)
                            close_ticker_postion(ticker)
                            trade_sell_stocks(ticker,hourly_closing_price+atr_value)
                        
                            
            


            elif pos_df[pos_df["name"]==ticker]["position"].values[0] < 0 :
                print('we have current ticker in position and is short')
                logging.info('we have current ticker in position and is short')
                hourly_closing_price=hist_df_hourly['close'].iloc[0]
                atr_value=hist_df_daily['atr'].iloc[-1]
                buy_condition=hist_df_hourly['super'].iloc[-1]>0 and hist_df_daily['ema'].iloc[-1]<hist_df_hourly['close'].iloc[-1]
                # buy_condition=True
                # current_balance=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))
                # if current_balance>hist_df.close.iloc[-1]:
         
                if buy_condition:
                            print('buy condiiton satisfied')
                            logging.info('buy condiiton satisfied')
                            close_ticker_open_orders(ticker)
                            close_ticker_postion(ticker)
                        
                            trade_buy_stocks(ticker,hourly_closing_price-atr_value)
       




logging.info('Strategy started')

current_time=datetime.datetime.now()
print(current_time)

print(datetime.datetime.now())

start_time=datetime.datetime(current_time.year,current_time.month,current_time.day,start_hour,start_min)
end_time=datetime.datetime(current_time.year,current_time.month,current_time.day,end_hour,end_min)
print(start_time)
print(end_time)

logging.info('Checking if start time has been reached')
while start_time>datetime.datetime.now():
    print(datetime.datetime.now())
    time.sleep(1)

logging.info('Starting the main code')

candle_size=60
# main_strategy_code()

logging.info('Starting the main code with candle size'+str(candle_size))
while datetime.datetime.now()<end_time:
    main_strategy_code()
    now = datetime.datetime.now()
    print(now)
    seconds_until_next_minute = candle_size - now.second+1
    print(seconds_until_next_minute)
    # Sleep until the end of the current minute
    time.sleep(seconds_until_next_minute)

    # Run your function
    

logging.info('Stragegy ended')
print(datetime.datetime.now())
print('Strategy ended')



