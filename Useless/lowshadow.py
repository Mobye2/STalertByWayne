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

for i in range(0,len(hislist)):
    pf = pd.read_csv(path + '/newhistory/' + hislist.iat[i, 0], thousands=',',index_col='日期')
    #print(pf.loc[[twstrdate]])

    try:
        if pf.at[twstrdate, "開盤價"] > pf.at[twstrdate, "收盤價"]:
            loshadow = (pf.at[twstrdate, "收盤價"] - pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
            #print('綠下影線=', loshadow)
        else:
            loshadow = (pf.at[twstrdate, "開盤價"] - pf.at[twstrdate, "最低價"]) / pf.at[twstrdate, "開盤價"]
            #print('紅下影線=', loshadow)
        if loshadow > 0.03:
            print(hislist.iat[i, 0],'有長下影線',round(loshadow,2) )
    except:
        pass

    


