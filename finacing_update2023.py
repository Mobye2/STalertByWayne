import os
import pandas as pd
import datetime


def datetoTWslash(date):
    date = str(date)
    date = date.replace('-', "/")
    date = date.replace('2022', "111", 1)
    return date


def date_get_today(with_time=False):
    '''
    取得今日日期，並指定為台北時區
    '''
    import pytz
    central = pytz.timezone('Asia/Taipei')

    if with_time == True:
        now = datetime.datetime.now(central)
    else:
        now = datetime.datetime.now(central).date()
    return now


def beforenine():
    date = datetime.datetime.now()
    end_time = datetime.datetime.strptime('21:00:00', "%H:%M:%S")
    realdate = (date.hour - end_time.hour) < 0
    return realdate


path = os.getcwd()
todate = date_get_today()
# todate=todate-datetime.timedelta(days=1)
if beforenine() == True:
    todate = todate-datetime.timedelta(days=1)
if todate.weekday() == 6:
    todate = todate - datetime.timedelta(days=2)
strtodate = todate.strftime('%Y-%m-%d')
hislist = pd.read_csv(path+'/historylist.csv', encoding='utf-8-sig')

stock_nolist = []
for i in range(0, len(hislist)):
    hislists = hislist.iat[i, 0].split()
    stock_nolist.append(hislists[1])
print(todate)
# 下載新資料並篩選
link = 'https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN'
newfina = pd.read_json(link)
# print (newfina)
for i in range(0, len(stock_nolist)):  #
    # 讀入歷史資料
    data = pd.read_csv(path+"/112newfinancing/" +
                       stock_nolist[i]+"stock_financing.csv", index_col=0)

    # 今日資料僅保留i股票
    filt = newfina['股票代號'] == stock_nolist[i]
    print(stock_nolist[i])
    thenewfina = pd.DataFrame(newfina.loc[filt])

    # 重新reset INDEX，使第一欄為0後更改名稱為日期
    thenewfina = thenewfina.reset_index(drop=True)
    thenewfina = thenewfina.rename(index={0: todate})
    count = 0
    # 刪除同天資料
    try:
        data = data.drop(index=[strtodate])
        count = count+1
        # print('count=', count)
    except:
        pass

    if count >= 1:
        print('skip')
        continue

    result = pd.concat([data, thenewfina])
    # print (result)

    result.to_csv(path+"/112newfinancing/" +
                  stock_nolist[i]+"stock_financing.csv", encoding='utf-8-sig')

'''
    #並聯方法
    stockfi=stockfi.rename(columns={'0':date})
    print (stockfi)
    stockfi2=stockfi
    stockfi2=stockfi2.rename(columns={date:tomorrow})
    df_outer = stockfi.merge(stockfi2, how='outer', left_index=True, right_index=True)
    print(df_outer)
    df_outer.to_csv('test.csv',encoding='utf-8-sig')
'''
