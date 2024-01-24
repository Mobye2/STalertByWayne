import pandas as pd
import os
name = 'stocklist'
# 讀取歷史資料檔名列表
path = os.getcwd()
indir = path
filename = '/historylist.csv'
fostocklist = pd.read_csv(indir+filename, thousands=',')


def kd_passavation(data, x):  # kd值三日鈍化判斷
    if data.at[x, 'k'] > 0.8 and data.at[x-1, 'k'] > 0.8 and data.at[x-2, 'k'] > 0.8 and data.at[x-3, 'k'] < 0.8:
        kd = True
    else:
        kd = False
    return kd


def low_shadow(data, x, thres):  # 下影線3%判斷
    lowerprice = min(data.at[x, "開盤價"], data.at[x, "收盤價"])
    loshadow = (lowerprice - data.at[x, "最低價"]) / data.at[x, "開盤價"]
    thres = thres*0.01
    if loshadow > thres:
        shadow = True
    else:
        shadow = False
    return shadow


def up_shadow(data, x):  # 上影線3%判斷
    higherprice = max(data.at[x, "開盤價"], data.at[x, "收盤價"])
    upshadow = (data.at[x, "最高價"]-higherprice) / data.at[x, "開盤價"]
    if upshadow > 0.03:
        upshadowj = True
    else:
        upshadowj = False
    return upshadowj


def volume_explode(data, x, multi):
    ave_volume = data['成交股數'].mean()
    if data.at[x, "成交股數"] > multi*ave_volume:  # 低於平均交易量的1倍
        explode = True
    else:
        explode = False
    return explode


def MAlowsupport(data, x):
    # 20MA有支撐
    if data.at[x-2, '20MA'] < data.at[x-2, '收盤價'] and data.at[x-1, '20MA'] < data.at[x-1, '收盤價'] and data.at[x, '最低價'] <= data.at[x, '20MA'] < data.at[x, '收盤價']:
        MAlowsupportJ = True
    else:
        MAlowsupportJ = False
    return MAlowsupportJ


def MApass(data, x):

    if data.at[x-2, '20MA'] > data.at[x-2, '收盤價'] and data.at[x-1, '20MA'] > data.at[x-1, '收盤價'] and data.at[x, '20MA'] < data.at[x, '收盤價']:
        MApassJ = True
    else:
        MApassJ = False
    return MApassJ


def MAGap(data, x):
    a = data.at[x, '20MA']-data.at[x, '5MA']
    return a


def MAcross(data, x, magapday):  # x為日期 n為20MA-5MA，由負轉正的追蹤日

    p = 0
    for i in range(0, magapday):
        if MAGap(data, x-i) < MAGap(data, x-i-1):
            p += 1
        else:
            break
    if MAGap(data, x-1) > 0 and MAGap(data, x) < 0:
        p += 1
    if p == magapday+1:
        MAGapJ = True
    else:
        MAGapJ = False
    return MAGapJ


win = 0
lose = 0
totalaveprofit = []

thresperc = 7  # 買賣門檻值

for thresperc in range(4, 9):
    thresperc += 1
    thres = thresperc*0.01
    count = 0
    for i in range(0, len(fostocklist)):  # len(fostocklist)

        hisfilename = fostocklist.iat[i, 0]
        # print(hisfilename)
        data = pd.read_csv(path+'/112kdnewhistory/'+hisfilename,
                           thousands=',')  # , index_col=0
        stockprofit = []
        saleday = 0
        for x in range(10, len(data)-10):
            list = []
            # print("kd_passavation=", kd_passavation(data, x))
    # 賣出後才可再買入
            if x < saleday:
                continue
    # 指定購入條件
            # 上影線+交易量<平均交易量，勝率57%，多頭時期88%
            # multi = 1  # n倍交易量為門檻
            # if up_shadow(data, x) == True and volume_explode(data, x, multi) == False:
                #    and data.at[x, '收盤價'] > data.at[x, '開盤價']
            # MA交叉 MAgapday追蹤天數 高勝率
            # if MAcross(data, x, 4) == True:
                # low_shadow(data, x, 3) == True:
            # KD鈍化
            if MAlowsupport(data, x) and volume_explode(data, x, 2):
                buyprice = data.at[x+1, '開盤價']
                count += 1
    # 賣出條件_漲跌達7%
                d = 0

                while ((data.at[x + d, '收盤價']-buyprice)/buyprice) < thres and ((data.at[x + d, '收盤價']-buyprice)/buyprice) > thres*-1 and x+d < len(data)-10:
                    d += 1
                    # print((len(data)-11), x, d)
                    # print(data.at[x + d, '收盤價'])
                    saleday = x+d+1
                saleprice = data.at[x+d+1, '開盤價']
                # 排除因為到資料最後一天賣
                if x+d == (len(data)-10):
                    continue

            # 獲利與勝率統計
                tradeprofit = round((saleprice - buyprice) / buyprice * 100, 2)
                if tradeprofit > 0:
                    win += 1
                else:
                    lose += 1
                stockprofit.append(tradeprofit)
                # profit[j] = round(((data.at[j + 5, '收盤價']) - todayprice),2)# / todayprice) * 100
                # print('購買日期與價格=', data.at[x, '日期'], buyprice,
                #       ',超過', thres*100,  '%的日期=', data.at[x+d, '日期'], '價格與差值=', saleprice, tradeprofit)

        aveprofit = sum(stockprofit) / (len(stockprofit) + 0.0001)
        # try:
        #     print('average profit=', aveprofit, 'winning rate=',
        #           win/(win+lose), '交易次數=', count)
        # except:
        #     pass
        totalaveprofit.append(aveprofit)
    print('threshold=', thres, 'winning rate=',
          win/(win+lose), '交易次數=', count)
    # avetotalprofit = sum(totolaveprofit) / (len(totolaveprofit) + 0.0001)
    # print ('total average profit=',aveprofit)
    filt = [n for n in totalaveprofit if n < -0.01 or n > 0.01]
    # print("==============================\n所有股票收益=", filt)
    # print('filt=', filt)
    if len(filt) > 0:
        print('所有股票平均收益=', sum(filt) / len(filt))


'''
    for j in range(0,len(data)):
        #print (data.at[j,'日期'])
        if data.at[j,'日期']=='2023/01/03':
        #    print (data.at[j, '日期'])
            data.at[j, '日期'] = data.at[j,'日期'].replace(
                '2023/01/03', "112/01/03", 1)
        #    print(data.at[j, '日期'])
    print (data)

    data.to_csv(path + '/20230104/' + hisfilename,
                encoding='utf-8-sig', index_label=0)
    data['filter']=filter
    data.drop(data[data['filter']==True].index,inplace=True)
    print (data)
    data.to_csv(path+'/20230104/'+hisfilename,encoding='utf-8-sig',index_label=0)
    '''
