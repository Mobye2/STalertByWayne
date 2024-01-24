import requests
import pandas as pd
import numpy as np
import datetime
import os


def conv_to_list(obj):
    '''
    將物件轉換為list
    '''
    if not isinstance(obj, list):  # isinstance() 函数来判断一个对象是否是一个已知的类型，类似 type() TRUE OR FALSE
        results = [obj]
    else:
        results = obj
    return results


def df_conv_col_type(df, cols, to, ignore=False):
    '''
    一次轉換多個欄位的dtype
    '''
    cols = conv_to_list(cols)
    for i in range(len(cols)):
        if ignore:
            try:
                df[cols[i]] = df[cols[i]].astype(to)
            except:
                print('df_conv_col_type - ' + cols[i] + '轉換錯誤')
                continue
        else:
            df[cols[i]] = df[cols[i]].astype(to)
    return df


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


def datetoTWslash(date):
    date = str(date)
    date = date.replace('-', "/")
    date = date.replace('2023', "112", 1)
    return date


def beforeend():
    date = datetime.datetime.now()
    end_time = datetime.datetime.strptime('14:00:00', "%H:%M:%S")
    realdate = (date.hour - end_time.hour) < 0
    return realdate


def KD(final):
    list = []
    k = final.at[len(final) - 2, 'k']
    d = final.at[len(final) - 2, 'k']
    for y in range(1, 10):
        list.append(final.at[len(final) - y, '最高價'])
        list.append(final.at[len(final) - y, '最低價'])
    # RSV = (第n天收盤價 - n天內最低價) / (n天內最高價 - n天內最低價) * 100 %
    # K = 1 / 3(RSV) + 2 / 3(昨日K值)
    # D = 1 / 3(K值) + 2 / 3(昨日D值)
    # (如果無前一日的K值或D值，則用50%代入)
    rsv = (final.at[len(final)-1, '收盤價'] - min(list)) / (max(list) - min(list))
    k = 1 / 3 * rsv + 2 / 3 * k
    d = 1 / 3 * k + 2 / 3 * d
    # print('rsv=', rsv)
    # print('k=', k, 'd=', d)
    final.at[len(final)-1, 'rsv'] = rsv
    final.at[len(final)-1, 'k'] = k
    final.at[len(final)-1, 'd'] = d
    # print (final)
    return final


def MA(data):
    fiveMA = data['收盤價'].tail(5).mean()
    tenMA = data['收盤價'].tail(10).mean()
    twentyMA = data['收盤價'].tail(20).mean()
    data.at[len(data)-1, '5MA'] = fiveMA
    data.at[len(data)-1, '10MA'] = tenMA
    data.at[len(data)-1, '20MA'] = twentyMA
    return data


# 下載證交所資料 ------
path = os.getcwd()
link = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=open_data'
data = pd.read_csv(link)

'''
# ['證券代號', '證券名稱', '成交股數', '成交金額', '開盤價',
#  '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']
data.columns = ['STOCK_SYMBOL', 'NAME', 'TRADE_VOLUME', 'TRADE_VALUE',
                'OPEN', 'HIGH' ,'LOW', 'CLOSE', 'PRICE_CHANGE', 'TRANSACTION']
'''
# 依今日交易結果存檔
date = date_get_today()  # 2022-12-20
if beforeend() == True:
    date = date-datetime.timedelta(days=1)
strdate = str(date)
data.to_csv(path+"/daystock/"+strdate+'daystock.csv',
            index=False, encoding='utf-8-sig')
print(strdate)
# 從歷史資料檔名列表取得股號
hislist = pd.read_csv(path+'/historylist.csv', encoding='utf-8-sig')
stock_nolist = []
for i in range(0, len(hislist)):
    hislists = hislist.iat[i, 0].split()
    stock_nolist.append(hislists[1])

for i in range(0, len(stock_nolist)):  # len(stock_nolist)
    # 從今日交易結果data保留選擇的個股資料
    print(stock_nolist[i])
    filt = data['證券代號'] == stock_nolist[i]
    keptdata = pd.DataFrame(data.loc[filt].drop('證券代號', axis=1))
    keptdata = keptdata.drop('證券名稱', axis=1)
    try:
        keptdata['日期'] = datetoTWslash(strdate)
    except:
        pass
    # 將各股今日交易結果聯集到歷史資料
    historydata = pd.read_csv(
        path+'/112kdnewhistory/'+hislist.iat[i, 0], thousands=',')
    final = pd.concat([historydata, keptdata]).reset_index()
    final = final.drop('index', axis=1)

    # 如果有重複資料 直接結束迴圈
    net = ['成交股數', '成交金額', '開盤價']
    repeat = final.duplicated(subset=net, keep=False)  # 標註重複資料
    # print(repeat)
    count = 0
    for r in repeat:
        if r == True:
            # print('repeat')
            count = count+1
            # print('count=', count)
    if count >= 1:
        print('repeat, loop pass')
        continue

    final = KD(final)
    final = MA(final)
    # print(final)
    todir = path+'/112kdnewhistory/'
    tofilename = hislist.iat[i, 0]
    final.to_csv(todir+tofilename, encoding='utf-8-sig', index=None)


'''
    # 依欄位判定資料重複則DROP
    net = ['日期']
    final.drop_duplicates(subset=net, keep='last', inplace=True)
    final = final.reset_index(drop=True)


    # 如果有重複日期先DROP
    dateTW = datetoTWslash(strdate)
    # print(historydata)
    indexNames = final[final['日期'] == dateTW].index
    final.drop(indexNames, inplace=True)

    '''
# 計算KD值


'''


'''

'''
filt=(data['證券代號'].isin(s))
focusdata=pd.DataFrame(data.loc[filt])
print (focusdata)
#focusdata.to_csv('')

'''
