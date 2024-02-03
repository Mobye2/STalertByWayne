import pandas as pd
import os
import datetime
import requests
import time
import random
import comfunc as cf

global path
path = os.getcwd()
global todate
todate = datetime.datetime.now()


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
    # print('今日價=', todayprice)
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


def finAlert(path, stock_no, strtodate, stryesdate):
    Finmessage2 = tuple()
    try:
        findata = pd.read_csv(path + "/112newfinancing/" +
                              stock_no + "stock_financing.csv", index_col=0)
        findelta = findata.at[strtodate, '融資前日餘額'] - \
            findata.at[strtodate, '融資今日餘額']
        perc = findelta / findata.at[strtodate, '融資今日餘額']
        if perc > 0.15:
            Finmessage2 = 'financing sold=', findelta, '(', round(
                perc, 2)*100, '%)'
    except:
        findata = pd.read_csv(path + "/112newfinancing/" +
                              stock_no + "stock_financing.csv", index_col=0)
        findelta = findata.at[stryesdate, '融資前日餘額'] - \
            findata.at[stryesdate, '融資今日餘額']
        perc = findelta / findata.at[stryesdate, '融資今日餘額']
        if perc > 0.15:
            Finmessage2 = 'financing sold=', findelta, '(', round(
                perc, 2)*100, '%)'
            # print(stryesdate,message2)
        # print('投信無大買賣')
    return Finmessage2


def alert(stock_no, stock_name, periodhigh, todayprice, yesprice, periodlow):
    samedays = []
    plsamedays = []
    message = tuple()
    message1 = tuple()
    ''''''
    for k in range(0, len(periodhigh)):
        # try:

        if todayprice <= (periodhigh.at[k, 'lhprice'] * 1.00) and yesprice > (periodhigh.at[k, 'lhprice'] * 1.01):
            periodhigh.at[k, 'lhcount'] = periodhigh.at[k, 'lhcount'] + 1
            date = periodhigh.at[k, 'lhdate'].strftime('%Y-%m-%d')
            samedays.append(date)
            # else:
            # print('no periodhigh ')
        # except:
         #   print('periodhigh pass')
          #  pass
    if len(samedays) != 0:
        message = 'high threshold,as', samedays
        print(message)
    '''period low'''
    for k in range(0, len(periodlow)):

        try:
            if todayprice <= (periodlow.at[k, 'plprice'] * 1.00) and yesprice > (periodlow.at[k, 'plprice'] * 1.01):
                periodlow.at[k, 'plcount'] = periodlow.at[k, 'plcount'] + 1
                date = periodlow.at[k, 'pldate'].strftime('%Y-%m-%d')
                plsamedays.append(date)

        except:
            print(stock_no, stock_name, 'pl pass')
            pass
    if len(plsamedays) != 0:
        message1 = 'low threshold, as', plsamedays

    twomes = message+message1
    return twomes


def periodpeak(path, filename):
    # 依證券號碼取得峰值指標檔案
    periodhigh = pd.read_csv(
        path+'/periodhigh/' + filename+"periodhigh.csv", thousands=",")  # thounsands可以去千位符號
    periodlow = pd.read_csv(
        path+'/periodlow/'+filename+"periodlow.csv")
    # 只查看最近N天內的指標
    filtday = 60
    periodhigh = filtph(filtday, todate, periodhigh)
    periodlow = filtpl(filtday, todate, periodlow)
    return periodhigh, periodlow


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
        if loshadow > 0.03:
            print(stockname, '有長下影線', round(loshadow, 2))
            ShadowAlert = '有長下影線=', round(loshadow, 2)
    except:
        print(stockname, 'shadow pass')
        pass
    return ShadowAlert


def volume_explode(histortdataI):
    Vmesseage = tuple()
    ave_volume = histortdataI['成交股數'].mean()
    y = len(historydataI)-1
    if histortdataI.at[y, "成交股數"] > 1*ave_volume:  # 超過平均交易量的1倍
        VExplodeJ = True
    else:
        VExplodeJ = False
        Vmesseage = ',', "交易量小於平均"
    return VExplodeJ, Vmesseage


def upshadow(pf, twstrdate, historydataI):
    ShadowAlert = tuple()

    if pf.at[twstrdate, "開盤價"] > pf.at[twstrdate, "收盤價"]:
        upshadow = (pf.at[twstrdate, "最高價"] -
                    pf.at[twstrdate, "開盤價"]) / pf.at[twstrdate, "開盤價"]
    else:
        upshadow = (pf.at[twstrdate, "最高價"] -
                    pf.at[twstrdate, "收盤價"]) / pf.at[twstrdate, "開盤價"]
    if upshadow > 0.03:
        # 上影線+交易量小於平均值、7%即交易=>勝率54%，多頭時期78%
        historydataI = pf.reset_index()
        VExplodeJ, Vmesseage = volume_explode(historydataI)
        ShadowAlert = '有長上影線=', round(upshadow, 2), Vmesseage
        # except:
        #     print(stockname, 'shadow pass')
        #     pass
    return ShadowAlert


def kdkpassive(historydataI):
    # 原序號為時間，調整序號為編號
    list = []
    messeage = tuple()
    for y in range(1, 5):
        list.append(historydataI.at[len(historydataI) - y, 'k'])
    # print (list,sum(list))
    if list[0] > 0.8 and list[1] > 0.8 and list[2] > 0.8 and list[3] < 0.8:
        # print('kd的k值鈍化alert' )
        messeage = '\n', 'KD的k值鈍化alert!!'
    return messeage


def MAlowtouch(historydataI):
    messeage = tuple()
    # 原序號為時間，調整序號為編號
    x = len(historydataI)
    try:
        if historydataI.at[x-3, '20MA'] < historydataI.at[x-3, '收盤價'] and historydataI.at[x-2, '20MA'] < historydataI.at[x-2, '收盤價'] and historydataI.at[x-1, '最低價'] < historydataI.at[x-1, '20MA'] < historydataI.at[x-1, '收盤價']:
            messeage = '/n', '20MA有支撐'
    except:
        pass
    return messeage


def MAGap(historydataI, x):
    a = historydataI.at[x, '20MA']-historydataI.at[x, '5MA']
    return a


def MAcross(historydataI, magapday):  # MA交叉，連續n日縮小最後翻正
    messeagMG = tuple()
    x = len(historydataI)-1
    p = 0
    for i in range(0, magapday):
        if MAGap(historydataI, x-i) < MAGap(historydataI, x-i-1):
            p += 1
        else:
            break
    if MAGap(historydataI, x-1) > 0 and MAGap(historydataI, x) < 0:
        p += 1
    if p == magapday+1:
        MAcrossJ = True
        messeagMG = '\n', 'MA交叉'
        # messeagMG = tuple(messeagMG)
    else:
        MAcrossJ = False
    return MAcrossJ, messeagMG


'''
====================================main=====================================
'''

# 讀取歷史資料檔名列表
filename = '/historylist.csv'
fostocklist = pd.read_csv(path+filename, thousands=',')

# 依列表序取得檔名
for i in range(0, len(fostocklist)):  # len(fostocklist)
    # 打開歷史資料並取得今日與昨日金額
    hisfilename = fostocklist.iat[i, 0]
    fulldir = path+'/112kdnewhistory/'+hisfilename
    historydata = pd.read_csv(fulldir, thousands=',', index_col="日期")
    todate, strtodate, twstrtodate, yesdate, stryesdate, twstryesdate = workday(
        historydata, todate)
    todayprice, yesprice = getprice(historydata, twstrtodate, twstryesdate)
# 取得個股編號與名稱
    hisfilename = hisfilename.split()
    stock_no = hisfilename[1]
    stock_name = hisfilename[2]
    filename = stock_no+stock_name
    historydataI = historydata.reset_index()
# 取得峰值檔案
    periodhigh, periodlow = periodpeak(path, filename)
# 峰值告警
    twomes = alert(
        stock_no, stock_name, periodhigh, todayprice, yesprice, periodlow)
# 融資告警
#    Finmessage2 = finAlert(path, stock_no, strtodate, stryesdate)
# 下影線告警
    loShadowAlert = lowshadow(historydata, twstrtodate, stock_no+stock_name)
# 上影線告警
    upShadowAlert = upshadow(historydata, twstrtodate, stock_no+stock_name)
# KD值鈍化告警
    kdmesseage = kdkpassive(historydataI)
# MA支撐告警
    MAsupmes = MAlowtouch(historydataI)
# MA黃金交叉
    MAGapJ, messeagMG = MAcross(historydataI, 4)
    comMes = twomes + upShadowAlert + \
        messeagMG + kdmesseage   # + Finmessage2+ MAsupmes+ loShadowAlert

# 印出結果與LINE告警機制
    print(hisfilename)
    if len(comMes) > 1:
        stinfo = tuple()
        stinfo = twstrtodate, '\n', stock_no, stock_name, '\n'
        finalMes = stinfo + comMes
        print(finalMes)

        token = 'YirsvmhRjT15zQMuSrEihN4i3upGFFJaulP9F6ly2EE'
        lineNotifyMessage(token, finalMes)


'''

'''
