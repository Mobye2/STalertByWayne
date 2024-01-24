import pandas as pd
import requests
import json
import time
import random
import os
from datetime import datetime
import comfunc as cf


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


def lowshadow(pf, twstrdate, stockname):
    ShadowAlert = tuple()
    try:
        if pf.at[twstrdate, "開盤價"] > pf.at[twstrdate, "收盤價"]:
            loshadow = (pf.at[twstrdate, "最高價"] -
                        pf.at[twstrdate, "收盤價"]) / pf.at[twstrdate, "開盤價"]
            # print('綠下影線=', loshadow)
        else:
            loshadow = (pf.at[twstrdate, "開盤價"] -
                        pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
            # print('紅下影線=', loshadow)
        if loshadow > 0.03:
            print(stockname, '有長下影線', round(loshadow, 2))
            ShadowAlert = '有長下影線=', round(loshadow, 2)
    except:
        print(stockname, 'shadow pass')
        pass
    return ShadowAlert


# 要更新的月份
# date = 20230101
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

    # 取得自有歷史資料
    thehistory = pd.read_csv(path+'/112kdnewhistory/' +
                             hislist.iat[i, 0])
    # print(thehistory)
    # ave_volume = thehistory['成交股數'].mean()
    # print(ave_volume)
    twenty = thehistory.tail(20)
    thehistory['5MA'] = thehistory['收盤價'].rolling(5).mean()
    thehistory['10MA'] = thehistory['收盤價'].rolling(10).mean()
    thehistory['20MA'] = thehistory['收盤價'].rolling(20).mean()
    # print(thehistory)
    # for j in range(20, len(thehistory)):
    #     ma5 = thehistory.rolling(5).mean()

    #     twentyMA = data.at[j,'收盤價'].tail(20).mean()
    # sixtyMA = data['收盤價'].tail(60).mean()
    # data.at[len(data)-1, '20MA'] = twentyMA
    # data.at[len(data)-1, '60MA'] = sixtyMA
    print(path+'/112newhistory/' +
          hislist.iat[i, 0], 'historyMA')
    # print(thehistory)
    thehistory.to_csv(path+'/112kdnewhistory/' +
                      hislist.iat[i, 0], index=None, encoding='utf-8-sig')
