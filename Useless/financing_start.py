import os
import pandas as pd
import datetime


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

def gethislist_stock_no():
    hislist = pd.read_csv(path + '/historylist.csv', encoding='utf-8-sig')
    stock_nolist = []
    for i in range(0, len(hislist)):
        hislists = hislist.iat[i, 0].split()
        stock_nolist.append(hislists[1])
    return stock_nolist

path = os.getcwd()
date= date_get_today()
tomorrow=date+datetime.timedelta(days=1)
date=str(date)
tomorrow=str(tomorrow)

stock_no_list=gethislist_stock_no()
print (stock_no_list)

link = 'https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN'
data = pd.read_json(link)
data.to_csv(path+"/financing/"+date+"stock_fiancing.csv", index=False, encoding='utf-8-sig')
data=data.drop(columns=["融資買進","融資賣出","融資現金償還","融資限額","融券買進","融券賣出","融券現券償還","融券限額","資券互抵","註記"],axis=1)
print (data)

for i in range(0,len(stock_no_list)):
    stock_no=stock_no_list[i]
    print (stock_no)
    filt=data['股票代號']==stock_no
    thedata=data.loc[filt]
    print (thedata)

    thedata=thedata.reset_index()
    thedata=thedata.rename(index={0:date})

    thedata.to_csv(path+"/financing/"+stock_no+"stock_fiancing.csv", encoding='utf-8-sig')

'''

'''