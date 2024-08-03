#open range breakout strategy
import pandas as pd
import datetime 
import time
from ib_insync import *
import pandas as pd
import pandas_ta as ta

import logging
logging.basicConfig(level=logging.INFO, filename=f'open_range_{datetime.date.today()}',filemode='w',format="%(asctime)s - %(message)s")

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=18)


try:
    order_filled_dataframe=pd.read_csv('order_filled_list.csv')
    order_filled_dataframe.set_index('time',inplace=True)

except:
    column_names = ['time','ticker','price','action']
    order_filled_dataframe = pd.DataFrame(columns=column_names)
    order_filled_dataframe.set_index('time',inplace=True)






# tickers=["COALINDIA","CIPLA","BRITANNIA","BPCL","BAJAJFINS",
# "BAJAJ-AUT","AXISBANK","ASIANPAIN","ADANIPORT"]
# tickers = ["WIPRO","ULTRACEMC","UPL","TITAN","TATASTEEL"]
# ,

# "TATAMOTOR","TCS","SUNPHARMA","SBIN","SHREECEM","RELIANCE","POWERGRID",
# "ONGC","NESTLEIND","NTPC"

# ,"MARUTI","KOTAKBANK","JSWSTEEL","INFY",
# "INDUSINDB",
# "IOC","ITC","ICICIBANK","HDFCBANK","HINDUNILV","HINDALCO",
# "HEROMOTOC","HCLTECH","GRASIM","GAIL","EICHERMOT","DRREDDY",
# "COALINDIA","CIPLA","BRITANNIA","BPCL","BAJAJFINS",
# "BAJAJ-AUT","AXISBANK","ASIANPAIN","ADANIPORT"]


tickers = ['GOOG']
exchange='SMART'
currency='USD'
account_no='DU8663688'

ord_validity='DAY'
quantity_=1
#start time
start_hour,start_min=0,8
#end time
end_hour,end_min=0,29



contract_objects={}
for ticker in tickers:
    c=ib.qualifyContracts(Stock(ticker,exchange, currency))[0]
    print(c)
    contract_objects[ticker]=c
print(contract_objects)



def order_open_handler(order):
    global order_filled_dataframe
    if order.orderStatus.status=='Filled':
        print('order filled')
        logging.info('order filled')
        name=order.contract.localSymbol
        a=[name,order.orderStatus.avgFillPrice,order.order.action]
        # if name not in order_filled_dataframe.ticker.to_list():
        order_filled_dataframe.loc[order.fills[0].execution.time] = a
        order_filled_dataframe.to_csv('order_filled_list.csv')
        message=order.contract.localSymbol+" "+order.order.action+"  "+str(order.orderStatus.avgFillPrice)
        logging.info(message)

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
    start_range=datetime.datetime(ct.year, ct.month, ct.day, 19, 0)
    end_range=datetime.datetime(ct.year, ct.month, ct.day, 20, 0)
    
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

def check_market_order_placed(name):
    ord=ib.reqAllOpenOrders()

    if ord:
        ord_df=pd.DataFrame(ord)
        print(ord_df)
        print(type(ord_df))
        # ord_df.to_csv('order_list.csv')
        ord_df['name']=[c['localSymbol'] for c in list(ord_df['contract'])]
        ord_df['ord_type']=[c['orderType']for c in list(ord_df['order'])]
        a=ord_df[(ord_df['name']==name) & (ord_df['ord_type']=='MKT') ]
        print(a)
        if a.empty:
            return True

        else:
            return False
    else:
        return True



def trade_sell_stocks(stock_name,stock_price,stop_price): #closing_price, quantitys=1  ????


    #market order
    global current_balance
    #market order
    contract = contract_objects[stock_name]
    # ord=MarketOrder(action='SELL',totalQuantity=1,AccountValue=account_no)
    if check_market_order_placed(stock_name):
       
        ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action='SELL',account=account_no,tif=ord_validity)
        trade=ib.placeOrder(contract,ord)
        ib.sleep(1)
        logging.info(trade)
        logging.info('Placed market sell order')

    else:
        logging.info('market order already placed')
        print('market order already placed')
        return 0



    # trailing order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.account=account_no
    order.action = 'BUY'
    order.orderType = "TRAIL"
    order.totalQuantity = quantity_
    order.auxPrice = 3
    order.trailStopPrice = int(stop_price)
    order.tif = ord_validity
    trade=ib.placeOrder(contract, order)
    ib.sleep(1)
    logging.info(trade)
    logging.info("placed stop order")



def trade_buy_stocks(stock_name,stock_price,stop_price):


    #market order
    contract = contract_objects[stock_name]
    # ord=MarketOrder(action='BUY',totalQuantity=1)
    if check_market_order_placed(stock_name):
        ord=Order(orderId=ib.client.getReqId(),orderType='MKT',totalQuantity=quantity_,action='BUY',account=account_no,tif=ord_validity)
        trade=ib.placeOrder(contract,ord)
        ib.sleep(1)
        logging.info(trade)
        logging.info('Placed market buy order')

    else:
        logging.info('market order already placed')
        print('market order already placed')
        return 0        



    # trailing order
    order = Order()
    order.orderId = ib.client.getReqId()
    order.account=account_no
    order.action = 'SELL'
    order.orderType = "TRAIL"
    order.totalQuantity = quantity_
    order.auxPrice = 3
    order.trailStopPrice = int(stop_price)
    order.tif = ord_validity
    trade=ib.placeOrder(contract, order)
    ib.sleep(1)
    logging.info(trade)
    logging.info("placed stop order")


def strategy(data,ticker,high_level,low_level):
    logging.info('inside strategy')
    print(ticker)
    print(data)
    
    buy_condition=data['close'].iloc[-1]>high_level
    buy_condition=True
    sell_condition=data['close'].iloc[-1]<low_level
    # sell_condition=True
    current_balance=int(float([v for v in ib.accountValues(account=account_no) if v.tag == 'AvailableFunds' ][0].value))

    if current_balance>data.close.iloc[-1]:
        if buy_condition:
            logging.info('buy condiiton satisfied')
            trade_buy_stocks(ticker,data.close.iloc[-1],low_level)
        elif sell_condition:
            logging.info('sell condition satisfied')
            trade_sell_stocks(ticker,data.close.iloc[-1],high_level)
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

    for ticker in tickers:
        logging.info(ticker)
        print('ticker name is',ticker,'################')
        ticker_contract=contract_objects[ticker]
        hist_df=get_historical_data(ticker_contract)
        high_level,low_level=get_level(hist_df)
        print(high_level, low_level)
        logging.info(f"{high_level} {low_level}")


        print(hist_df.tail(50))
        print(hist_df.close.iloc[-1])
        # ib.sleep(200)
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
ib.newOrderEvent += order_open_handler
ib.orderStatusEvent += order_open_handler
ib.cancelOrderEvent += order_open_handler

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




