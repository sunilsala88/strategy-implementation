from ib_insync import *
util.startLoop()  

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=17)




cont=ib.qualifyContracts(Stock('TSLA','SMART','USD'))[0]
print(cont)
d=ib.reqFundamentalData(cont,reportType='ReportSnapshot')
print(d)


path = 'data.xml'
with open(path, 'w') as f:
    f.write(d)
