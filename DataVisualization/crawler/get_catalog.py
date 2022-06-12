import random
import time
import requests

url = 'https://data.stats.gov.cn/easyquery.htm?cn=C01&id=zb&dbcode=hgnd&wdcode=zb&m=getTree'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
}


def sleep():
    """
    休眠策略

    :return: None
    """
    t = random.randint(1, 5)
    print(f"休眠{t}秒")
    time.sleep(t)


def run():
    r = requests.get(url=url, headers=headers, verify=False)
    # 综合、国民经济、人口等一栏
    level_1 = r.json()
    with open('level1.txt', 'w') as f:
        f.write(str(level_1))
        f.close()

    level_2 = []
    level_3 = []
    for i, item in enumerate(level_1):
        item_url = f'https://data.stats.gov.cn/easyquery.htm?cn=C01&id={item["id"]}&dbcode=hgnd&wdcode=zb&m=getTree'
        sleep()
        item_children = requests.get(url=item_url, headers=headers, verify=False)
        level_2.append({item['id']: item_children.json()})
        print(f'{item["name"]}已获取，已经获取第{i}个')
        for j, itm in enumerate(item_children.json()):
            if itm['isParent']:
                itm_url = f'https://data.stats.gov.cn/easyquery.htm?cn=C01&id={itm["id"]}&dbcode=hgnd&wdcode=zb&m=getTree'
                sleep()
                i_children = requests.get(url=itm_url, headers=headers, verify=False)
                level_3.append({itm['id']: i_children.json()})
                print(f'{itm["name"]}已获取，已经获取第{j}个')

    with open('level2.txt', 'w') as f1, open('level3.txt', 'w') as f2:
        f1.write(str(level_2))
        f2.write(str(level_3))
        f1.close()
        f2.close()


run()
