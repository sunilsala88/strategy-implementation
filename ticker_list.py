

from ib_insync import *


ib = IB()
ib.connect('127.0.0.1', 7497, clientId=18)


tickers = ["COALINDIA", "CIPLA", "BRITANNIA", "BPCL", "BAJAJFINS", "AXISBANK", "ASIANPAIN", "ADANIPORT", "WIPRO", "ULTRACEMC", "UPL", "TITAN", "TATASTEEL",
           "TATAMOTOR", "TCS", "SUNPHARMA", "SBIN", "SHREECEM", "RELIANCE", "POWERGRID", "NESTLEIND", "NTPC",
           "MARUTI", "KOTAKBANK", "JSWSTEEL", "INFY", "INDUSINDB", "ITC", "ICICIBANK", "HDFCBANK", "HINDUNILV", 
           "HINDALCO","HEROMOTOC", "HCLTECH", "GRASIM", "EICHERMOT", "DRREDDY","MM",
            "ADANIENT","APOLLO","DIVISLAB","HDFCLIFE","LT","SBILIFE", "TECHM","TATACONSU","LTTS" ,"SHRIRAMFI"]

#remove duplicates fro list
# print(len(tickers))


tickers=['MMM', 'AXP','AMGN', 'AMZN', 'AAPL', 'BA', 'CAT', 'CVX', 'CSCO', 'KO', 'DIS', 'DOW', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'MCD', 'MRK', 'MSFT', 'NKE', 'PG', 'CRM', 'TRV', 'UNH', 'VZ', 'V', 'WMT']
print(len(tickers))


exchange='SMART'
currency='USD'
account_no='DU8663688'


contract_objects={}
for ticker in tickers:
    c=ib.qualifyContracts(Stock(ticker,exchange, currency))
    print(c)
    c=c[0]
    contract_objects[ticker]=c
print(contract_objects)
