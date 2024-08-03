from ib_insync import *
util.startLoop()  

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=17)

sub = ScannerSubscription(
    instrument='STOCK.HK', 
    locationCode='STK.HK.NSE', 
    scanCode='TOP_VOLUME_RATE')

scanData = ib.reqScannerData(sub)

print(f'{len(scanData)} results, first one:')
print(scanData[0])
df=util.df(scanData)
print(df)
print(df.columns)
df['name']=[cont.contract.symbol for cont in df['contractDetails']]
print(df)


# xml = ib.reqScannerParameters()

# print(len(xml), 'bytes')

# path = 'scanner_parameters.xml'
# with open(path, 'w') as f:
#     f.write(xml)

# import webbrowser
# webbrowser.open(path)

# # parse XML document
# import xml.etree.ElementTree as ET
# tree = ET.fromstring(xml)

# # find all tags that are available for filtering
# tags = [elem.text for elem in tree.findall('.//AbstractField/code')]
# print(len(tags), 'tags:')
# print(tags)

# print(tags)

# locationCodes = [e.text for e in tree.findall('.//locationCode')]
# print(locationCodes)


cont=ib.qualifyContracts(Stock('RELIANCE','NSE','INR'))[0]
print(cont)
d=ib.reqFundamentalData(cont,reportType='ReportSnapshot')
print(d)


path = 'data.xml'
with open(path, 'w') as f:
    f.write(d)

