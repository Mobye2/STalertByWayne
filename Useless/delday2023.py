#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import os
import datetime
import requests
path = os.getcwd()
# 讀取歷史資料檔名列表
indir = path
filename = '/historylist.csv'
fostocklist = pd.read_csv(indir+filename, thousands=',')

# delete finacing
'''
for i in range(0,len(fostocklist)):#
    hisfilename = fostocklist.iat[i, 0]
    hisfilename=hisfilename.split()
    #print (hisfilename[1])

    indir = path + '/newfinancing/'
    fulldir = indir + hisfilename[1]+'stock_fiancing.csv'
    print (fulldir)
    data=pd.read_csv(fulldir,thousands=',',index_col=0)
    filter=data.index=='2023-01-02'
    data['filter']=filter
    data.drop(data[data['filter']==True].index,inplace=True)
    print (data)
    data.to_csv(path+'/20230104/'+hisfilename[1]+'stock_fiancing.csv',encoding='utf-8-sig',index_label=0)
'''

# delete trade
for i in range(0, len(fostocklist)):  #
    hisfilename = fostocklist.iat[i, 0]
    print(hisfilename)
    name = hisfilename.split(' ')
    st_no = name[1]
    # print(st_no)
    data = pd.read_csv(path+'/112kdnewhistory/'+hisfilename,
                       thousands=',', index_col=None,encoding='utf-8-sig')
    
    # 刪除指定日期資料
    dates_to_drop = ["113/02/06", "113/02/16"]
    data = data[~data['日期'].isin(dates_to_drop)]

    # Delete the column with Unnamed
    data = data.loc[:, ~data.columns.str.contains('0')]
    #print (data)

    # print(data)
    data.to_csv(path+'/112kdnewhistory/'+hisfilename,
                encoding='utf-8-sig', index=False)
'''
    # 刪除FINACING資料用
    data = pd.read_csv(path+'/newfinancing/'+st_no+'stock_fiancing.csv',
                       thousands=',', index_col=0)
    net = ['融資前日餘額', '融券今日餘額', '融券買進']
    data.drop_duplicates(subset=net, keep='first', inplace=True)
    # data.drop_duplicates(inplace=True)
    print(data)
    data.to_csv(path+'/112newfinacing/'+st_no+'stock_financing.csv',
                encoding='utf-8-sig', index_label=0)
                    '''

    

