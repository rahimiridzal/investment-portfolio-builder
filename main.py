import numpy as np
import pandas as pd
import requests
import xlsxwriter

#keep stock symbols and names, data will be extracted from IEX Cloud
stocks = pd.read_csv('sp500stocks.csv')[['Symbol', 'Description']]
##print(stocks)

#specify column names for final output
column_names = ['Ticker', 'Stock Names', 'Market Cap.', 'No. of Stocks to Buy']
df = pd.DataFrame(columns=column_names)
print(df)