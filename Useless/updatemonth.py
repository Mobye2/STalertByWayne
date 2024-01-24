import pandas as pd
import requests
import json
import time
import random
import os


def urltjason(url):
    user_agent = {'User-agent': 'Chrome/107.0.0.0'}
    r = requests.get(url,  headers=user_agent)
    print(r, '狀態回應')
    list_of_dicts = r.json()
    # print (list_of_dicts)
    return (list_of_dicts)


def getstockdata(date, stock_no):
    html = urltjason(
        'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=%s&stockNo=%s' % (date, stock_no))
    stock_data = html['data']
    col_name = html['fields']
    global stockname
    stockname = html['title']
    return pd.DataFrame(data=stock_data, columns=col_name)


def historydata(date, enddate, stockdata, stock_no):
    for i in range(1, 5):  # 累積<5年資料
        for j in range(1, 13):
            print(date)
            stockdata = stockdata.append(getstockdata(date, stock_no))
            time.sleep(random.uniform(3, 6))
            date = date + 100
            if date > enddate:
                break
        date = date + 10000 - 1200
        if date > enddate:
            break
    return stockdata


def makehistorylist(historylistdir):
    # 建立歷史資料檔名列表historylist
    historylistdir = historylistdir
    historylist = pd.DataFrame(os.listdir(historylistdir))
    print(historylist)
    historylist.to_csv("historylist.csv", index=False, encoding='utf-8-sig')


# 要更新的月份
date = 20230101
path = os.getcwd()
# 歷史檔案清單與清單內股票代號
hislist = pd.read_csv(path+'/historylist.csv', encoding='utf-8-sig')
stock_nolist = []
for i in range(0, len(hislist)):  # len(hislist)
    hislists = hislist.iat[i, 0].split()
    # print (hislists,hislists[1])
    stock_nolist.append(hislists[1])
stock_nolist = pd.DataFrame(stock_nolist)

for i in range(0, len(hislist)):  # len(hislist)
    # 取得指定月份資料
    # print(stock_nolist)
    print(stock_nolist.iat[i, 0])  # 股票編號
    stock_no = stock_nolist.iat[i, 0]
    print('https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=%s&stockNo=%s' %
          (date, stock_no))
    stockdata = getstockdata(date, stock_no)
    stockdata.drop(stockdata.index)  # 整理格式
    list = stockdata['日期']
    # print(stockdata)
    # print('list=', list)

    # 取得自有歷史資料
    thehistory = pd.read_csv(path+'/kdnewhistory/'+hislist.iat[i, 0])

    # 刪除既有指定月份資料
    for j in list:
        indexNames = thehistory[thehistory['日期'] == j].index
        thehistory.drop(indexNames, inplace=True)

    # append指定月份資料
    thehistory = thehistory.append(stockdata)

    # 刪除多餘欄位
    thehistory.drop(thehistory.columns[thehistory.columns.str.contains(
        '0  ', case=False)], axis=1, inplace=True)

    thehistory.to_csv(path+'/112newhistory/' +
                      hislist.iat[i, 0], index=False, encoding='utf-8-sig')
    print('休息3-6秒')
    time.sleep(random.uniform(3, 6))
