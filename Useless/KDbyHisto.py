import pandas as pd
import os
name = 'stocklist'
a = []
path = os.getcwd()
# 讀取歷史資料檔名列表
indir = path
filename = '/historylist.csv'
fostocklist = pd.read_csv(indir+filename, thousands=',')


# turn days trade
for i in range(0, 1):  # len(fostocklist)
    k = 0.5
    d = 0.5
    hisfilename = fostocklist.iat[i, 0]
    print(hisfilename)
#   name = hisfilename.split(' ')
#    print(name[1])
    data = pd.read_csv(path+'/112newhistory/'+hisfilename,
                       thousands=',')
    # print(data)
    # print(data.at[8, '最高價'])
    data = data.drop('rsv', axis=1)
    data = data.drop('k', axis=1)
    data = data.drop('d', axis=1)
    # print(data)
    net = ['成交股數', '成交金額']
    data.drop_duplicates(subset=net, keep='first', inplace=True)
    # data.drop_duplicates(inplace=True)
    data.reset_index(drop=True, inplace=True)
    # print('clean data=', data)

    for x in range(8, len(data)):
        list = []
        for y in range(0, 9):
            list.append(data.at[x - y, '最高價'])
            list.append(data.at[x - y, '最低價'])
        # RSV = (最近第n天收盤價 - 最近n天內最低價) / (最近n天內最高價 - 最近n天內最低價) * 100 %
        # K = 1 / 3(RSV) + 2 / 3(昨日K值)
        # D = 1 / 3(K值) + 2 / 3(昨日D值)
        # (如果無前一日的K值或D值，則用50%代入)
        rsv = (data.at[x, '收盤價']-min(list))/(max(list)-min(list))
        k = 1/3*rsv+2/3*k
        d = 1 / 3 * k + 2 / 3 * d
        # print('rsv=', rsv)
        # print('k=', k, 'd=', d)
        data.at[x, 'rsv'] = rsv
        data.at[x, 'k'] = k
        data.at[x, 'd'] = d
    # print(data.tail(15))
    # print(data.head(15))
    data.to_csv(path+'/112kdnewhistory/'+hisfilename, encoding='utf-8-sig')
    # print(data)


'''
    for j in range(0, len(data)):
        # print (data.at[j,'日期'])
        if data.at[j, '日期'] == '2023/01/03':
        #    print (data.at[j, '日期'])
            data.at[j, '日期'] = data.at[j, '日期'].replace(
                '2023/01/03', "112/01/03", 1)
        #    print(data.at[j, '日期'])
    print(data)

    data.to_csv(path + '/20230104/' + hisfilename,
                encoding='utf-8-sig', index_label=0)
    data['filter'] = filter
    data.drop(data[data['filter'] == True].index, inplace=True)
    print(data)
    data.to_csv(path+'/20230104/'+hisfilename,
                encoding='utf-8-sig', index_label=0)
    '''
