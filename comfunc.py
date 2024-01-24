import os
import pandas as pd
import datetime


def packages():
    import os
    import pandas as pd
    import datetime


def gethislist():
    path = os.getcwd()
    hislist = pd.read_csv(path + "/historylist.csv", encoding="utf-8-sig")
    stock_nolist = []
    for i in range(0, len(hislist)):
        hislists = hislist.iat[i, 0].split()
        stock_nolist.append(hislists[1])
    return hislist, stock_nolist


def gettodate():
    todate = datetime.datetime.now()
    strdate = todate.strftime("%Y-%m-%d")
    return todate, strdate


def datetoTWslash(date):
    date = str(date)
    date = date.replace("-", "/")
    date = date.replace("2029", "118", 1)
    date = date.replace("2028", "117", 1)
    date = date.replace("2027", "116", 1)
    date = date.replace("2026", "115", 1)
    date = date.replace("2025", "114", 1)
    date = date.replace("2024", "113", 1)
    date = date.replace("2023", "112", 1)
    date = date.replace("2022", "111", 1)

    return date
