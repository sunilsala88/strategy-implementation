
from ib_insync import *
util.startLoop()  

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=17)

sub = ScannerSubscription(
    instrument='STK', 
    locationCode='STK.US.MAJOR', 
    scanCode='TOP_PERC_GAIN')

scanData = ib.reqScannerData(sub)

print(f'{len(scanData)} results, first one:')
print(scanData)


df=util.df(scanData)
print(df)
print(df.columns)
df['name']=[cont.contract.symbol for cont in df['contractDetails']]
print(df)