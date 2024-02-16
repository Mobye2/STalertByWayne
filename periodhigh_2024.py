import pandas as pd
import os


def readcsvgetpf(indir, infilename):
    infulldir = indir + infilename
    #print(infulldir)
    pf = pd.read_csv(infulldir, thousands=",")  # thounsands可以去千位符號
    #print(pf)
    for i in range(0, len(pf)):  # 民國轉西元
        pf.at[i, '日期'] = pf.at[i, '日期'].replace('111', '2022')
        pf.at[i, '日期'] = pf.at[i, '日期'].replace('112', '2023')
        pf.at[i, '日期'] = pf.at[i, '日期'].replace('113', '2024')
        pf.at[i, '日期'] = pf.at[i, '日期'].replace('114', '2025')
    pf['日期'] = pd.to_datetime(pf['日期']).dt.date
    finalprice = pf[['收盤價']]
    return pf[['日期']], pf[['收盤價']]


def makephlist():
    phlist = {
        "lhdate": [],
        "lhprice": [],
        "lhcount": []
    }
    phlist = pd.DataFrame(phlist)
    return phlist


def fillphlist(period, finalprice, tdate, phlist):
    for i in range(period, len(finalprice) - period):
        beforehigh = finalprice.iat[i - 1, 0]
        afterhigh = finalprice.iat[i + 1, 0]
        # print (finalprice.iat[i,0])
        for j in range(0, period):  # 是否為前後五天的最大值
            if finalprice.iat[i - 1 - j, 0] > beforehigh:
                beforehigh = finalprice.iat[i - 1 - j, 0]
            if finalprice.iat[i + 1 + j, 0] > afterhigh:
                afterhigh = finalprice.iat[i + 1 + j, 0]
        # print ('前後五天最大值為=',beforehigh,afterhigh ,'今天值為=',pf.at[i, '日期'],finalprice.iat[i,0])

        # 將峰值存入列表
        if beforehigh < finalprice.iat[i, 0] and afterhigh < finalprice.iat[i, 0]:
            phlist = phlist.append({
                'lhdate': tdate.iat[i, 0],
                'lhprice': finalprice.iat[i, 0],
                "lhcount": 0
            }, ignore_index=True)
            #print('最新新高發生在=', tdate.iat[i, 0], finalprice.iat[i, 0])
    return phlist


def savedata(data, infilename, outdir):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    x = infilename.split()
    outfilename = x[1] + x[2] + 'periodhigh' + '.csv'
    fulldir = outdir + outfilename
    #print(fulldir)
    data.to_csv(fulldir, index=False, encoding='utf-8-sig')


path = os.getcwd()

# 取得歷史資料檔名列表
historylistdir = path
infilename = pd.read_csv(historylistdir+"/historylist.csv",
                         thousands=",")  # thounsands可以去千位符號
#print(infilename.iat[0, 0])

# 依歷史列表的檔名依序計算指標
for i in range(0, len(infilename)):
    # 讀個股歷史資料並取得日期與價格列表
    historydatadir = path+'/112kdnewhistory/'
    tdate, finalprice = readcsvgetpf(historydatadir, infilename.iat[i, 0])
    #print(tdate, finalprice)
    print (infilename.iat[i, 0])
    # 建立空白個股指標表
    phlist = makephlist()
    period = 5  # 價格是前後period天的峰值
    # 計算個股指標表
    phlist = fillphlist(period, finalprice, tdate, phlist)
    outdir = path+'/periodhigh/'
    savedata(phlist, infilename.iat[i, 0], outdir)
    #print(phlist)
