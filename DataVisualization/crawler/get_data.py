import json
import random
import time
import numpy as np
import requests
import pandas as pd


def read_file():
    # 读取目录
    with open('level1.txt', 'r') as f1, open('level2.txt', 'r') as f2, open('level3.txt', 'r') as f3:
        l1 = f1.read()
        l2 = f2.read()
        l3 = f3.read()
        f1.close()
        f2.close()
        f3.close()

    data_headlines = []
    lst_1 = eval(l1)
    lst_2 = eval(l2)
    lst_3 = eval(l3)

    for item in lst_1:
        if item['isParent']:
            continue
        data_headlines.append(item)

    for item in lst_2:
        for values in item.values():
            for value in values:
                if not value['isParent']:
                    data_headlines.append(value)

    for item in lst_3:
        for values in item.values():
            for value in values:
                if not value['isParent']:
                    data_headlines.append(value)
    return data_headlines


# print(data_headlines)

# 取前10条记录测试，测试数据
# test = [data_headlines[i] for i in range(10)]

# 取人民生活
test = [i for i in read_file() if i['pid'] == "A0A"]


def get_time():
    """
    :return: 13 位时间戳
    """
    return int(round(time.time() * 1000))


def sleep():
    """
    随机休眠（1~5秒）策略

    :return: None
    """
    t = random.randint(1, 5)
    print(f"休眠{t}秒")
    time.sleep(t)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
}


def run():
    for item in test:
        params = {'m': 'QueryData', 'dbcode': 'hgnd', 'rowcode': 'zb', 'colcode': 'sj', 'wds': '[]',
                  'dfwds': '[{"wdcode": "zb", "valuecode": "%s"}]' % item['id'], 'k1': str(get_time()), 'h': '1'}
        sleep()
        r = requests.get('https://data.stats.gov.cn/easyquery.htm', headers=headers, params=params, verify=False)
        js = json.loads(r.text)

        data = [data['data']['strdata'] for data in js['returndata']['datanodes']]

        # 转换为二维数组
        array = np.array(data).reshape(len(data) // 10, 10)
        df = pd.DataFrame(array)

        df.index = [node['name'] + "(" + node['unit'] + ")" for node in js['returndata']['wdnodes'][0]['nodes']]
        df.columns = [node['name'] for node in js['returndata']['wdnodes'][1]['nodes']]
        new_df = df.dropna()
        print(new_df)
        new_df.to_csv('csv/%s.csv' % item['name'])

# run()
