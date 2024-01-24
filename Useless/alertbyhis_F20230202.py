import pandas as pd
import os
import datetime
import requests
import time
import random
import comfunc as cf


def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify",
                      headers=headers, params=payload)
    return r.status_code


def workday(historydata, todate):
    strtodate = todate.strftime("%Y-%m-%d")
    twstrtodate = cf.datetoTWslash(strtodate)
    for i in range(0, 10):
        try:
            price = historydata.at[twstrtodate, '收盤價']
            break
        except:
            todate = todate - datetime.timedelta(days=1)
            strtodate = todate.strftime("%Y-%m-%d")
            twstrtodate = cf.datetoTWslash(strtodate)
    yesdate = todate - datetime.timedelta(days=1)
    stryesdate = yesdate.strftime('%Y-%m-%d')
    twstryesdate = cf.datetoTWslash(stryesdate)
    for i in range(0, 10):
        try:
            price = historydata.at[twstryesdate, '收盤價']
            break
        except:
            yesdate = yesdate - datetime.timedelta(days=1)
            stryesdate = yesdate.strftime("%Y-%m-%d")
            twstryesdate = cf.datetoTWslash(stryesdate)
    return todate, strtodate, twstrtodate, yesdate, stryesdate, twstryesdate


def getprice(historydata, twstrtodate, twstryesdate):
    # 取得今日價

    # print (historydata)
    todayprice = historydata.at[twstrtodate, '收盤價']
    todayprice = float(todayprice)

    yesprice = historydata.at[twstryesdate, '收盤價']
    yesprice = float(yesprice)

    return todayprice, yesprice


def filtph(filtday, todate, periodhigh):
    deadline = todate - datetime.timedelta(days=filtday)
    # print (deadline)
    periodhigh['lhdate'] = pd.to_datetime(periodhigh['lhdate'])
    filter = periodhigh['lhdate'] > deadline
    # print(filter)
    periodhigh['filter'] = filter
    periodhigh.drop(periodhigh[periodhigh['filter']
                    == False].index, inplace=True)
    return periodhigh.reset_index()


def filtpl(filtday, todate, periodlow):
    deadline = todate - datetime.timedelta(days=filtday)
    # print (deadline)
    periodlow['pldate'] = pd.to_datetime(periodlow['pldate'])
    filter = periodlow['pldate'] > deadline
    # print(filter)
    periodlow['filter'] = filter
    periodlow.drop(periodlow[periodlow['filter'] == False].index, inplace=True)
    return periodlow.reset_index()


def alert(stock_no, stock_name, periodhigh, todayprice, yesprice, periodlow):
    samedays = []
    plsamedays = []
    message = tuple()
    message2 = tuple()
    ''''''
    for k in range(0, len(periodhigh)):
        # print (todayprice,'vs',periodhigh.at[k, 'lhprice'],yesprice)
        try:
            if todayprice <= (periodhigh.at[k, 'lhprice'] * 1.00) and yesprice > (periodhigh.at[k, 'lhprice'] * 1.01):
                periodhigh.at[k, 'lhcount'] = periodhigh.at[k, 'lhcount'] + 1
                # if periodhigh.at[k, 'lhcount'] <= 2:
                date = periodhigh.at[k, 'lhdate'].strftime('%Y-%m-%d')
                samedays.append(date)
            # else:
            # print ('try work')
        except:
            print('periodhigh pass')
            pass
    if len(samedays) != 0:
        message = 'high threshold,as', samedays
        # print (message)
    '''period low'''
    for k in range(0, len(periodlow)):
        # print (todayprice,'vs',periodhigh.at[k, 'lhprice'],yesprice)
        try:
            if todayprice <= (periodlow.at[k, 'plprice'] * 1.00) and yesprice > (periodlow.at[k, 'plprice'] * 1.01):
                periodlow.at[k, 'plcount'] = periodlow.at[k, 'plcount'] + 1
                # if periodhigh.at[k, 'lhcount'] <= 2:
                date = periodlow.at[k, 'pldate'].strftime('%Y-%m-%d')
                plsamedays.append(date)
                # else:
                #    print ('try work')
        except:
            print(stock_no, stock_name, 'pl pass')
            pass
    if len(plsamedays) != 0:
        message1 = 'low threshold, as', plsamedays
        # print (message1)

    '''融資減少1%以上'''
    try:
        findata = pd.read_csv(path + "/112newfinancing/" +
                              stock_no + "stock_financing.csv", index_col=0)
        findelta = findata.at[strtodate, '融資前日餘額'] - \
            findata.at[strtodate, '融資今日餘額']
        perc = findelta / findata.at[strtodate, '融資今日餘額']
        if perc > 0.15:
            message2 = 'financing sold=', findelta, '(', round(
                perc, 2)*100, '%)'
            # print(strtodate,message2)
        # print('投信無大買賣')
    except:
        findata = pd.read_csv(path + "/112newfinancing/" +
                              stock_no + "stock_financing.csv", index_col=0)
        findelta = findata.at[stryesdate, '融資前日餘額'] - \
            findata.at[stryesdate, '融資今日餘額']
        perc = findelta / findata.at[stryesdate, '融資今日餘額']
        if perc > 0.15:
            message2 = 'financing sold=', findelta, '(', round(
                perc, 2)*100, '%)'
            # print(stryesdate,message2)
        # print('投信無大買賣')

    twomes = message+message2
    # print (almes)
    # print (len(almes))
    return twomes


def lowshadow(pf, twstrdate, stockname):
    ShadowAlert = tuple()
    try:
        if pf.at[twstrdate, "開盤價"] > pf.at[twstrdate, "收盤價"]:
            loshadow = (pf.at[twstrdate, "收盤價"] -
                        pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
            # print('綠下影線=', loshadow)
        else:
            loshadow = (pf.at[twstrdate, "開盤價"] -
                        pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
            # print('紅下影線=', loshadow)
        if loshadow > 0.04:
            print(stockname, '有長下影線', round(loshadow, 2))
            ShadowAlert = '有長下影線=', round(loshadow, 2)
    except:
        print(stockname, 'shadow pass')
        pass
    return ShadowAlert


def kdkpassive(historydata):
    historydata = historydata.reset_index()
    list = []
    messeage = tuple()
    for y in range(1, 5):
        list.append(historydata.at[len(historydata) - y, 'k'])
    # print (list,sum(list))
    if list[0] > 0.8 and list[1] > 0.8 and list[2] > 0.8:
        # print('kd的k值鈍化alert' )
        messeage = '\n', 'KD的k值鈍化alert!!'
    return messeage


'''
====================================main=====================================
'''
path = os.getcwd()
# 讀取歷史資料檔名列表
indir = path
filename = '/historylist.csv'
fostocklist = pd.read_csv(indir+filename, thousands=',')
# 取得日期(有資料的)
todate = datetime.datetime.now()
indir = path+'/112kdnewhistory/'
hisfilename = fostocklist.iat[1, 0]
fulldir = indir+hisfilename
historydata = pd.read_csv(fulldir, thousands=',', index_col="日期")
todate, strtodate, twstrtodate, yesdate, stryesdate, twstryesdate = workday(
    historydata, todate)

# 依列表序取得檔名
for i in range(0, len(fostocklist)):
    # 打開歷史資料並取得今日與昨日金額
    hisfilename = fostocklist.iat[i, 0]
    print(hisfilename)
    # print (hisfilename)
    indir = path+'/112kdnewhistory/'
    fulldir = indir+hisfilename
    historydata = pd.read_csv(fulldir, thousands=',', index_col="日期")
    # (historydata)
    todayprice, yesprice = getprice(historydata, twstrtodate, twstryesdate)

    # 依證券號碼取得指標並判定是否符合
    indir = path+'/periodhigh/'
    hisfilename = hisfilename.split()
    stock_no = hisfilename[1]
    stock_name = hisfilename[2]
    filename = stock_no+stock_name+"periodhigh.csv"
    periodhigh = pd.read_csv(
        indir + filename, thousands=",")  # thounsands可以去千位符號
    periodlow = pd.read_csv(
        path+'/periodlow/'+stock_no+stock_name+"periodlow.csv")
    # print (periodlow)
    # 查看融資
    # 只查看最近N天內的指標
    filtday = 60
    periodhigh = filtph(filtday, todate, periodhigh)
    periodlow = filtpl(filtday, todate, periodlow)
    twomes = alert(
        stock_no, hisfilename[2], periodhigh, todayprice, yesprice, periodlow)
    ShadowAlert = lowshadow(historydata, twstrtodate, stock_no+stock_name)
    kdmesseage = kdkpassive(historydata)
    comMes = twomes + kdmesseage+ShadowAlert
    token = 'YirsvmhRjT15zQMuSrEihN4i3upGFFJaulP9F6ly2EE'
    if len(comMes) > 1:
        stinfo = tuple()
        stinfo = twstrtodate, '\n', stock_no, stock_name, '\n'
        finalMes = stinfo + comMes
        print(finalMes)
        lineNotifyMessage(token, finalMes)


'''

'''
