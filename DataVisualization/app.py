from flask import Flask, render_template, jsonify
import pandas as pd
import os
import math

app = Flask(__name__)

# ------------------------变量-----------------------
# 测试数据
file_ = './static/csv/全国居民人均支出情况.csv'
# 文件列表
filename_list = [file.split('.')[0] for file in os.listdir('./static/csv')]
# print(filename_list)
filepath_list = ['./static/csv/' + file for file in os.listdir('./static/csv')]


# ------------------------路由-----------------------
@app.route('/')
def root():  # put application's code here
    return index()


@app.route('/index')
def index():
    return render_template('index.html', file_name=handle_file(filename_list))


@app.route('/tables')
def tables():
    return render_template('tables.html', data=get_data(file_), file_name=handle_file(filename_list))


@app.route('/table<ta_index>')
def table(ta_index):
    print(ta_index)
    # 合并之后文件名称
    names = handle_file(filename_list)
    print(names)

    # 合并数据
    df = merge_tables(names[int(ta_index)])
    column_name = [i for i in df.columns]
    row_name = [i for i in df.index]
    data = []
    for i in df.index:
        temp = []
        for j in df.loc[i]:
            temp.append(j)
        data.append(temp)
    # 清洗数据
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = delete_extra_zero(data[i][j])
            if math.isnan(data[i][j]):
                data[i][j] = ''
    return jsonify(name=names[int(ta_index)], column=column_name, rows=row_name, data=data)


@app.route('/charts')
def charts():
    return render_template('charts.html', file_name=handle_file(filename_list), share_name=filename_list)


@app.route('/chart<ch_index>')
def chart_dataset(ch_index):
    """处理图表数据请求"""
    return_table_path = select_tables(ch_index)
    data_list = [{
        "name": get_data(path)[0],
        "year": get_data(path)[1],
        "label": get_data(path)[2],
        "data": get_data(path)[3]
    }
        for path in
        return_table_path]
    # 三张表数据
    if len(data_list) == 3:
        return_data = []
        # 对三个表数据遍历，得到三个二维数组
        for item in data_list:
            temp = []
            # 对二维数组遍历
            for item_list in item['data']:
                item_sum = 0
                # 把二维数组中的每一个数组累加，组成一个一维数组
                for num in item_list:
                    # num如果是空串就转化为零
                    if num == '':
                        num = 0
                    item_sum += num
                temp.append(round(item_sum, 1))
            return_data.append(temp)
        resp = [['product', '全国居民', '农村居民', '城镇居民']]

        for i in range(len(return_data[0])):
            resp.append([data_list[0]['label'][i], return_data[0][i], return_data[1][i], return_data[2][i]])

        return jsonify(data_list, resp)
    else:
        if data_list[0]['name'] == '居民恩格尔系数':
            resp = [['product', '全国居民', '城镇居民', '农村居民']]
            for i in range(len(data_list[0]['data'][0])):
                resp.append([data_list[0]['year'][i], data_list[0]['data'][0][i], data_list[0]['data'][1][i],
                             data_list[0]['data'][2][i]])
            return jsonify(data_list, resp)
        elif data_list[0]['name'] == '居民人均可支配收入基尼系数':
            resp = [['product', '全国居民']]
            for i in range(len(data_list[0]['data'][0])):
                # 如果是空串就转化为零
                if data_list[0]['data'][0][i] == '':
                    data_list[0]['data'][0][i] = 0
                resp.append([data_list[0]['year'][i], data_list[0]['data'][0][i]])
            return jsonify(data_list, resp)
        else:
            # 最后一种表格数据
            resp = [['product']]
            for i in range(len(data_list[0]['label'])):
                resp[0].append(data_list[0]['label'][i])
            # 对二维数组遍历
            for i in range(len(data_list[0]['data'])):
                for item in data_list[0]['data'][i]:
                    # 如果是空串就转化为零
                    if item == '':
                        item = 0
                resp.append([data_list[0]['year'][i], data_list[0]['data'][i][0], data_list[0]['data'][i][1],
                             data_list[0]['data'][i][2], data_list[0]['data'][i][3], data_list[0]['data'][i][4]])
            return jsonify(data_list, resp)


@app.route('/track<track_index>')
def track(track_index):
    """对三类人员的总量计数"""
    paths = select_tables(track_index)

    table_data = [{
        "name": get_data(path)[0],
        "data": get_data(path)[3]} for path in paths]

    title = "近十年" + handle_file(filename_list)[int(track_index)] + "总量"

    # 对三类人员的总量计数
    resp = []
    if len(table_data) == 3:
        for j in range(3):
            num = 0
            if '支出' in table_data[j]['name'] or '收入' in table_data[j]['name']:
                for i in range(0, len(table_data[j]['data']), 2):
                    for item in table_data[j]['data'][i]:
                        if item == '':
                            item = 0
                        num += item
                resp.append(round(num, 1))
            else:
                for i in range(len(table_data[j]['data'])):
                    for item in table_data[j]['data'][i]:
                        if item == '':
                            item = 0
                        num += item
                resp.append(round(num, 1))
    else:
        if '居民恩格尔系数' in title:
            for row in table_data[0]['data']:
                num = 0
                for item in row:
                    num += item
                resp.append(round(num, 1))

    return jsonify(title=title, data=resp)


@app.route('/share<share_index>')
def share(share_index):
    """每张图表详细信息"""
    table_data = get_data(filepath_list[int(share_index)])
    resp_data = [['product']]
    for item in table_data[1]:
        resp_data[0].append(item)
    for i in range(len(table_data[2])):
        for j in range(len(table_data[3][i])):
            # 空串转0
            if table_data[3][i][j] == '':
                table_data[3][i][j] = 0
        resp_data.append([table_data[2][i]])
        resp_data[i + 1].extend(table_data[3][i])
    return jsonify(title=table_data[0], data=resp_data)


# ------------------------常用方法-----------------------
def get_data(file):
    """获取数据"""
    df = pd.read_csv(file, index_col=0)
    column_name = [i for i in df.columns]
    row_name = [i for i in df.index]
    data = []
    for i in df.index:
        temp = []
        for j in df.loc[i]:
            temp.append(j)
        data.append(temp)
    name = os.path.splitext(file)[0].split('/')[-1]
    # 清洗数据
    for i in range(len(data)):
        for j in range(len(data[i])):
            data[i][j] = delete_extra_zero(data[i][j])
            if math.isnan(data[i][j]):
                data[i][j] = ''

    return name, column_name, row_name, data


def delete_extra_zero(n):
    """删除小数点后多余的0"""
    n = str(n).rstrip('0')  # 删除小数点后多余的0
    n = int(n.rstrip('.')) if n.endswith('.') else float(n)  # 只剩小数点直接转int，否则转回float
    return n


def handle_file(file):
    """处理文件名"""
    re_field = ['全国居民', '农村居民', '城镇居民']
    field_set = set()
    for name in file:
        for field in re_field:
            if field in name:
                name = name.strip(field)
        field_set.add(name)
    return list(field_set)


def merge_tables(filename):
    """合并表"""
    data = []
    data_index = []
    field = ['农民工规模及收入主要数据', '居民恩格尔系数', '居民人均可支配收入基尼系数']
    if filename in field:
        return pd.read_csv('./static/csv/' + filename + '.csv', index_col=0)
    else:
        name1 = './static/csv/全国居民%s.csv' % filename
        name2 = './static/csv/农村居民%s.csv' % filename
        name3 = './static/csv/城镇居民%s.csv' % filename
        f1 = pd.read_csv(name1, index_col=0)
        f2 = pd.read_csv(name2, index_col=0)
        f3 = pd.read_csv(name3, index_col=0)
        for i in range(len(f1.values)):
            data.append(f1.values[i])
            data.append(f2.values[i])
            data.append(f3.values[i])
        for i in range(len(f1)):
            data_index.append(f1.index[i])
            data_index.append(f2.index[i])
            data_index.append(f3.index[i])
        df = pd.DataFrame(data, index=data_index, columns=f1.columns)
        return df


def select_tables(se_index):
    """选择表
    :return: 返回数据选中表的路径
    """
    file_name = handle_file(filename_list)
    return [item for item in filepath_list if file_name[int(se_index)] in item]


if __name__ == '__main__':
    app.run()
