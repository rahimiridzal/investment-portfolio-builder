import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

#keep stock symbols, other data will be extracted from IEX Cloud
stocks = pd.read_csv('sp500stocks.csv')['Symbol']
##print(stocks)

#specify column names for final output
column_names = ['Ticker', 'Company Name', 'Stock Price', 'Market Cap.', 'No. of Stocks to Buy']

#build DataFrame template with corresponding column names
df = pd.DataFrame(columns=column_names)
##print(df)

#from secrets.txt
IEX_CLOUD_API_TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'

#check on IEX Cloud API Reference page to get base url (for testing sandbox) and other required endpoints function
##api_url = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'

#the commented code below can identify cases where there exist stock(s) in the list from the csv file that its data cannot be extracted from IEX Cloud
#it uses Single API Call (slow)
"""
for i, ticker in enumerate(stocks):
    try:
        api_url = f'https://sandbox.iexapis.com/stable/stock/{ticker}/quote?token={IEX_CLOUD_API_TOKEN}'
        data = requests.get(api_url).json()
        #parse required data into proper format
        company_name = data['companyName']
        stock_price = data['latestPrice']
        market_cap = data['marketCap']
        #add data in right format to df
        df.loc[i,:] = [ticker, company_name, stock_price, market_cap, 'N/A']
        print(f"stock no: {i}")
    except Exception:
        print(f"data for {ticker} is not available")
        pass
print(df)
"""

#define function to group the element of a list in group of n or less
#needed because Batch API call can be executed for at most 100 stocks at a time
def group(a_list, n):
    for i in range(0, len(a_list), n):
        yield a_list[i:i+n]

grouped_stocks = list(group(stocks, 100))
##print(grouped_stocks)

#create a list of grouped stocks
grouped_stocks_list = []
for i in range(0, len(grouped_stocks)):
    grouped_stocks_list.append(','.join(grouped_stocks[i]))
##print(grouped_stocks_list)

#use Batch API Call(have tested that all stocks data are available)
index = 0
for one_group in grouped_stocks_list:
    batch_api_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={one_group}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_url).json()
    
    for ticker in one_group.split(','):
        company_name = data[ticker]['quote']['companyName']
        stock_price = data[ticker]['quote']['latestPrice']
        market_cap = data[ticker]['quote']['marketCap']
        df.loc[index,:] = [ticker, company_name, stock_price, market_cap, 'N/A']
        index += 1
##print(df)

while True:
    try:
        portfolio_size = float(input("\nEnter your portfolio size in US Dollar: $"))
    except ValueError:
        print("\nOps, sorry! Please enter a valid number.")
        continue
    else:
        break

while True:
    try:
        max_no_dif_stocks = int(input("\nEnter the maximum number of different stocks you want to have in your portfolio: "))
    except ValueError:
        print("\nSorry, can you try enter a valid integer again.")
    else:
        break

if max_no_dif_stocks > len(df.index):
    max_no_dif_stocks = len(df.index)

position_size = portfolio_size/max_no_dif_stocks

#drop not required stocks
df = df.iloc[:max_no_dif_stocks,:]
##print(df)

for i, stock_price in enumerate(df['Stock Price']):
    df.loc[i, 'No. of Stocks to Buy'] = math.floor(position_size/stock_price) #round-off to lower bound int
##print(df)

#initialise xlsxwriter
writer = pd.ExcelWriter('suggested_portfolio.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Suggested Portfolio', index=False)

#set format to be used in xlsx file
string_format = writer.book.add_format({'border': 1})
dollar_format = writer.book.add_format({'num_format':'$0.00','border': 1})
integer_format = writer.book.add_format({'num_format':'0','border': 1})

column_formats = {
    'A': ['Ticker', string_format],
    'B': ['Company Name', string_format],
    'C': ['Stock Price', dollar_format],
    'D': ['Market Cap.', dollar_format],
    'E': ['No. of Stocks to Buy', integer_format]
    }

for column in column_formats.keys():
    writer.sheets['Suggested Portfolio'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Suggested Portfolio'].write(f'{column}1', column_formats[column][0], string_format)

writer.save()

print("\nCongratulations! Your Investment Portfolio has been built.\n\nCheckout the suggested_portfolio.xlsx file.\n\nThank you for using our service and hope to see you again!\n\n")