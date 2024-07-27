import pandas as pd
import datetime 
import time
from ib_insync import *
import pandas as pd
import pandas_ta as ta

import logging
logging.basicConfig(level=logging.INFO, filename=f'orb_{datetime.date.today()}',filemode='w',format="%(asctime)s - %(message)s")

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=18)

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


#first hour
#previus day high low
#cpr top_cpr bottom cpr

def calculate_cpr(high, low, close):
    pivot = (high + low + close) / 3
    bc = (high + low) / 2
    tc = (pivot - bc) + pivot
    return pivot, bc, tc


def get_historical_data(ticker_contract):
    logging.info('fetching historical data')
    bars = ib.reqHistoricalData(
    ticker_contract, endDateTime='', durationStr=f'2 D',
    barSizeSetting='1 min', whatToShow='MIDPOINT', useRTH=True,formatDate=1)
    # convert to pandas dataframe:
    df = util.df(bars)
    print(df)

    logging.info('calculated indicators')
    
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


def trade_sell_stocks(stock_name,high_level): #closing_price, quantitys=1  ????
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
    order.auxPrice = int(high_level)
    order.tif = ord_validity
    order.account=account_no

    trade=ib.placeOrder(contract,order)
    ib.sleep(1)
    logging.info(trade)
    logging.info("placed stop order")
    



def trade_buy_stocks(stock_name,low_level):

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
    order.auxPrice = int(low_level)
    order.tif = ord_validity
    order.account=account_no

    trade=ib.placeOrder(contract,order)
    ib.sleep(1)
    logging.info(trade)
    logging.info("placed stop order")


def strategy(data,ticker,high_level,low_level):
    logging.info('inside strategy')
    print(ticker)
    print(data)
    
    buy_condition=data['close'].iloc[-1]>high_level
    # buy_condition=True
    sell_condition=data['close'].iloc[-1]<low_level
    # sell_condition=True
    current_balance=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))

    if current_balance>data.close.iloc[-1]:
        if buy_condition:
            logging.info('buy condiiton satisfied')
            trade_buy_stocks(ticker,data.close.iloc[-1])
        elif sell_condition:
            logging.info('sell condition satisfied')
            trade_sell_stocks(ticker,data.close.iloc[-1])
        else :
            logging.info('no condition satisfied')
    else:
        logging.info('we dont have enough money')
        logging.info('current balance is',current_balance,'stock price is ',data['close'].iloc[-1])


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
        hist_df=get_historical_data(ticker_contract)
        high_level,low_level=get_level(hist_df)
        print(high_level, low_level)
        logging.info(f"{high_level} {low_level}")

        print(hist_df)
        print(hist_df.close.iloc[-1])
        capital=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))
        print(capital)
        quantity=int((capital/10)/hist_df.close.iloc[-1])  
        print(quantity)
        logging.info('Checking condition')

        if quantity==0:
            logging.info('we dont have enough money so we cannot trade')
            continue

        if pos_df.empty:
            print('we dont have any position')
            logging.info('we dont have any position')
            strategy(hist_df,ticker,high_level,low_level)


        elif len(pos_df)!=0 and ticker not in pos_df['name'].tolist():
            logging.info('we have some position but current ticker is not in position')
            print('we have some position but current ticker is not in position')
            strategy(hist_df,ticker,high_level,low_level)




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





#closing all open orders
def close_all_orders():
    logging.info('closing all open orders')
    
    orders = ib.openOrders()
    print(orders)
    for order in orders:
        logging.info(order)
        a=ib.cancelOrder(order)
        logging.info(a)
    return 1
      
#closing all the open positions
def close_all_position():
    positions = ib.positions(account=account_no) # A list of positions, according to IB
    logging.info(positions)
    print('inside closing position')
    for position in positions:
        logging.info(position)
        print(position)
        n = position.contract.symbol
        # contract = position.contract
        contract=ib.qualifyContracts(Contract(conId=position.contract.conId))[0]
        print(contract)
        # c=ib.qualifyContracts(contract)[0]
        if position.position > 0: # Number of active Long positions
            action = 'SELL' # to offset the long positions
        elif position.position < 0: # Number of active Short positions
            action = 'BUY' # to offset the short positions
        totalQuantity = abs(position.position)
        logging.info(f'Flatten Position: {contract} {totalQuantity} {action}')
        # ord = MarketOrder(action=action, totalQuantity=totalQuantity)
        ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action=action,account=account_no,tif=ord_validity)
        trade = ib.placeOrder(contract, ord)
        logging.info(trade)

    return 1


 
close_all_orders()
close_all_position()
ib.disconnect()




