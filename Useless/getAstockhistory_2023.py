import pandas as pd
import requests, json
import time
import random
import os

def urltjason(url):
    user_agent = {'User-agent': 'Chrome/107.0.0.0'}
    r = requests.get(url,  headers = user_agent)
    print (r,'狀態回應')
    list_of_dicts = r.json()
    #print (list_of_dicts)
    return (list_of_dicts)

def getstockdata(date,stock_no):
    html = urltjason('https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=%s&stockNo=%s' % (date, stock_no))
    print(html)
    stock_data = html['data']
    col_name = html['fields']
    global stockname
    stockname= html['title']
    return pd.DataFrame(data=stock_data, columns=col_name)

def historydata(date,enddate,stockdata,stock_no):
    for i in range(1, 5):#累積<5年資料
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
    print (historylist)
    historylist.to_csv("historylist.csv", index=False, encoding='utf-8-sig')

#基本參數、欄位取得
path=os.getcwd()
date = 20220301
enddate=20221201
listofstock = pd.read_csv('STOCKLIST2.csv')


for i in range(0,len(listofstock)):
    print(listofstock.iat[i, 0])
    stock_no = listofstock.iat[i, 0]
    print('https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=%s&stockNo=%s' % (date, stock_no))
    # CALL API取得資料後刪除，留下欄位
    stockdata = getstockdata(date, stock_no)
    stockdata.drop(stockdata.index)
    time.sleep(random.uniform(3, 6))
    # 依日期、結束、起始、股票號碼取得歷史資料
    stockdata=historydata(date, enddate, stockdata, stock_no)

    filename = stockname + '.csv'
    stockdata.to_csv(path+'/historydata/'+filename,index=False, encoding='utf-8-sig')

# 建立歷史資料檔名列表檔
historydir=path+'/historydata/'
makehistorylist(historydir)