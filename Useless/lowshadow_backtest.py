import os
import pandas as pd
import datetime
import comfunc as cf

path=os.getcwd()
hislist,stock_nolist=cf.gethislist()
todate,strdate=cf.gettodate()
twstrdate=cf.datetoTWslash(strdate)
#print (hislist,'\n',stock_nolist)
#print (todate)
profit = []
for i in range(0,len(hislist)):#
    print (hislist.iat[i, 0])
    pf = pd.read_csv(path + '/newhistory/' + hislist.iat[i, 0], thousands=',',index_col='日期')
    todate, strdate = cf.gettodate()
    #print(pf.loc[[twstrdate]])
    for j in range(0,len(pf)):
        todate=todate-datetime.timedelta(days=1)
        if todate.weekday()==6:
            todate = todate - datetime.timedelta(days=2)
        twstrdate = cf.datetoTWslash(todate.strftime('%Y-%m-%d'))
        #print (twstrdate)
        try:
            #print ('open=',pf.at[twstrdate, "開盤價"] ,'close=', pf.at[twstrdate, "收盤價"])
            if pf.at[twstrdate, "開盤價"] > pf.at[twstrdate, "收盤價"]:
                loshadow = (pf.at[twstrdate, "收盤價"] - pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
                # print('綠下影線=', loshadow)
            else:
                loshadow = (pf.at[twstrdate, "開盤價"] - pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
                # print('紅下影線=', loshadow)
            #print (loshadow)
            if loshadow > 0.05:
                print(twstrdate,hislist.iat[i, 0], '有長下影線', round(loshadow, 3))
                selldate=todate+datetime.timedelta(days=7)
                twstrselldate = cf.datetoTWslash(selldate.strftime('%Y-%m-%d'))
                dayprofit = round(((pf.at[twstrselldate, '收盤價']) - pf.at[twstrdate, "收盤價"]) / pf.at[twstrdate, "收盤價"] * 100, 2)
                print (dayprofit)
                profit.append(dayprofit)
        except:
            pass

print ('ave profit=',sum(profit)/(len(profit)+1))


    


