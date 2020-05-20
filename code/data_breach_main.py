# -*- coding: utf-8 -*-
"""
Created on Wed May 29 08:51:37 2019

@author: Zhaoke

文件说明：运行决策树信度模型，绘制树结构图

参考代码：
https://github.com/shiluqiang/GBDT_regression
https://github.com/chandarb/Python-Regression-Tree-Forest
参考文献：
Diao L, Weng C. Regression Tree Credibility Model[J]. 
The North American Actuarial Journal, 2019, 23(2): 169-196.
"""

import pandas as pd
import os
import data_breach_cart_model as rp
import numpy as np
from datetime import datetime
from pyecharts.charts import Tree as plot_tree_by_py
from pyecharts import options as opts
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot as driver
import numpy
import math

'''
shell command
nohup python cart_combine_v2_log.py > cart_combine_v2_log_0403 2>&1 &
'''


# 获取全部csv文件名称
def csv_file_ops(path0, need_str0):
    # path0 = dir_path
    file_ops0 = []
    all_l = os.listdir(path0)
    for i_0 in range(len(all_l)):
        filetype = os.path.splitext(all_l[i_0])[1]
        if filetype == ".csv":
            filename = os.path.splitext(all_l[i_0])[0]
            if need_str0 in filename:
                file_ops0.append(path0 + all_l[i_0])
    return file_ops0


# l2损失函数（均方误差）
def loss_l2(data):
    if len(data[1]) == 0:
        return 0
    else:
        mean0 = np.mean(data[1])
        data1 = np.array(data[1])

    return np.sum((data1 - mean0) ** 2)


# 由文件名称获取数据集信息
def ops2info(ops_str):
    if "all" in ops_str:
        return "全部", "全部"

    ops_tmp = ops_str.split("/")[-1].split("_")

    return ops_tmp[2], ops_tmp[3][:-4]


# 计算信度理论的结构参数等
def dat2para(sc_dat):
    mi_l = []
    yi_l = []
    sigma0 = 0

    mi = [sc_dat[2][0][1]]
    yi = [sc_dat[1][0]]

    for u in range(len(sc_dat[2]) - 1):
        if sc_dat[2][u + 1][0] == sc_dat[2][u][0]:
            mi.append(sc_dat[2][u + 1][1])
            yi.append(sc_dat[1][u + 1])
        else:
            mi_l.append(sum(mi))
            yi_bar = np.dot(np.array(mi), np.array(yi)) / sum(mi)
            yi_l.append(yi_bar)
            fenmu = (len(yi) - 1)
            if fenmu == 0:
                # print("dat2para: ni=1, at risk!")
                fenmu = 0.0001
            s_tmp = np.dot((np.array(yi) - yi_bar) ** 2, np.array(mi)) / fenmu
            sigma0 = sigma0 + s_tmp
            mi = [sc_dat[2][u + 1][1]]
            yi = [sc_dat[1][u + 1]]
    mi_l.append(sum(mi))
    yi_bar = np.dot(np.array(mi), np.array(yi)) / sum(mi)
    yi_l.append(yi_bar)
    fenmu = (len(yi) - 1)
    if fenmu == 0:
        # print("dat2para: ni=1, at risk!")
        fenmu = 0.0001
    s_tmp = np.dot((np.array(yi) - yi_bar) ** 2, np.array(mi)) / fenmu
    sigma0 = sigma0 + s_tmp

    sigma0 *= float(1 / len(mi_l))

    m = sum(mi_l)
    y_bar = np.dot(np.array(yi_l), np.array(mi_l)) / m

    c_tmp = np.dot(np.array(mi_l) / m, (1 - np.array(mi_l) / m))
    if c_tmp == 0:
        c_tmp = 0.0001
    c = float(len(mi_l) - 1) / len(mi_l) * (c_tmp ** (-1))

    t_tmp = np.dot((np.array(yi_l) - y_bar) ** 2, np.array(mi_l) / m)
    fenmu = len(mi_l) - 1
    if fenmu == 0:
        fenmu = 0.0001
    tau0 = c * ((t_tmp * len(mi_l) / fenmu) - (sigma0 * len(mi_l) / m))
    tau0 = max(tau0, 0.0001)

    return sigma0, tau0, mi_l


# 非齐次信度保费I类损失(Regression Tree Credibility Model, (4.15式))
def loss_415(data_0):
    if len(data_0[1]) == 0:
        return 0

    sigma_k, tau_k, mi_k = dat2para(data_0)

    return np.sum(sigma_k * ((sigma_k / tau_k + np.array(mi_k)) ** (-1)))


# 非齐次信度保费II类损失(Regression Tree Credibility Model, (4.16式))
def loss_416(data_0):
    if len(data_0[1]) == 0:
        return 0

    sigma_k, tau_k, mi_k = dat2para(data_0)

    return np.sum(sigma_k * ((sigma_k / tau_k + np.array(mi_k)) ** (-1)) + sigma_k)


# 齐次信度保费I类损失(Regression Tree Credibility Model, (4.19式))
def loss_419(data_0):
    if len(data_0[1]) == 0:
        return 0

    sigma_k, tau_k, mi_k = dat2para(data_0)
    a_l = 1 - sigma_k / tau_k * (sigma_k / tau_k + np.array(mi_k)) ** (-1)
    alpha0 = max(float(np.sum(a_l)), 0.0000001)

    return tau_k * np.dot((1 - a_l), (1 + (1 - a_l) / alpha0))


# 齐次信度保费II类损失(Regression Tree Credibility Model, (4.20式))
def loss_420(data_0):
    if len(data_0[1]) == 0:
        return 0

    sigma_k, tau_k, mi_k = dat2para(data_0)
    a_l = 1 - sigma_k / tau_k * (sigma_k / tau_k + np.array(mi_k)) ** (-1)
    alpha0 = max(float(np.sum(a_l)), 0.0000001)

    return tau_k * np.dot((1 - a_l), (1 + (1 - a_l) / alpha0)) + sigma_k * len(mi_k)


# 计算预测误差
# sc_dat, balance0 = scale_test_data, balance
def cal_PE(sc_dat):
    # sc_dat = re_format(csv_data0, "all", balance0, fac_num0)
    mi_l = []
    yi_l = []
    sigma0 = 0

    mi = [sc_dat[2][0][1]]
    yi = [sc_dat[1][0]]

    for u in range(len(sc_dat[2]) - 1):
        if sc_dat[2][u + 1][0] == sc_dat[2][u][0]:
            mi.append(sc_dat[2][u + 1][1])
            yi.append(sc_dat[1][u + 1])
        else:
            mi_l.append(sum(mi))
            yi_bar = np.dot(np.array(mi), np.array(yi)) / sum(mi)
            yi_l.append(yi_bar)
            fenmu = (len(yi) - 1)
            if fenmu == 0:
                print("cal_PE: ni=1, it's wrong!")
                fenmu = 0.0001
            s_tmp = np.dot((np.array(yi) - yi_bar) ** 2, np.array(mi)) / fenmu
            sigma0 = sigma0 + s_tmp
            mi = [sc_dat[2][u + 1][1]]
            yi = [sc_dat[1][u + 1]]
    mi_l.append(sum(mi))
    yi_bar = np.dot(np.array(mi), np.array(yi)) / sum(mi)
    yi_l.append(yi_bar)
    fenmu = (len(yi) - 1)
    if fenmu == 0:
        print("cal_PE: ni=1, it's wrong!")
        fenmu = 0.0001
    s_tmp = np.dot((np.array(yi) - yi_bar) ** 2, np.array(mi)) / fenmu
    sigma0 = sigma0 + s_tmp

    sigma0 *= float(1 / len(mi_l))

    m = sum(mi_l)
    y_bar = np.dot(np.array(yi_l), np.array(mi_l)) / m

    c_tmp = np.dot(np.array(mi_l) / m, (1 - np.array(mi_l) / m))
    if c_tmp == 0:
        c_tmp = 0.0001
    c = float(len(mi_l) - 1) / len(mi_l) * (c_tmp ** (-1))

    t_tmp = np.dot((np.array(yi_l) - y_bar) ** 2, np.array(mi_l) / m)
    fenmu = len(mi_l) - 1
    if fenmu == 0:
        fenmu = 0.0001
    tau0 = c * ((t_tmp * len(mi_l) / fenmu) - (sigma0 * len(mi_l) / m))
    tau0 = max(tau0, 0.0001)

    a_l = 1 - (float(sigma0 / tau0) * ((sigma0 / tau0 + np.array(mi_l)) ** (-1)))
    ph_l = np.multiply(a_l, np.array(yi_l)) + ((1 - a_l) * y_bar)
    pe0 = np.sum((ph_l - np.array(yi_l)) ** 2)

    return pe0


# 计算相对预测误差
# tree0, sc_dat0, pe0, balance0 = tree_best, scale_test_data, PE0, balance
def cal_RPE(tree0, sc_dat0, pe0):
    sep_dat = tree0.to_part(sc_dat0)
    pe_t = 0

    for s in range(len(sep_dat)):
        pe_tmp = cal_PE(sep_dat[s])
        pe_t += pe_tmp

    rpe0 = pe_t / pe0

    return rpe0


# 计算普通分区的预测误差
# rule_rpe_list = cal_RPE_part(sc_dat0, pe0, balance0)
# sc_dat0, pe0, balance0 = scale_test_data, PE0, balance
def cal_RPE_part(sc_dat0, pe0):
    rule_l0 = [[1], [3], [0, 1, 2], [0, 1, 3], [1, 2, 3], [0, 2, 3], [0, 1, 2, 3]]
    r_name = ["R(2)", "R(4)", "R(123)", "R(124)", "R(234)", "R(134)", "R(1234)"]
    # rpe_l = []
    dict_rpe = {}

    for rl in range(len(rule_l0)):

        rule0 = rule_l0[rl]
        dat0 = [sc_dat0]
        for k in range(len(rule0)):
            dat_mid = []
            for d in dat0:
                dat_mid.extend(one2two(d, 50, rule0[k]))
            dat0 = dat_mid

        pe_t = 0

        for s in range(len(dat0)):
            pe_tmp = cal_PE(dat0[s])
            pe_t += pe_tmp

        rpe0 = pe_t / pe0
        # rpe_l.append(rpe0)
        dict_rpe[r_name[rl]] = rpe0

    return pd.DataFrame(dict_rpe, index=[0])


# 根据协变量分区
def one2two(data, split_point, split_var):
    # data, split_point, split_var = d, 0.5, rule0[k]
    # left
    data1 = [[], [], []]
    # right
    data2 = [[], [], []]

    for i0 in range(len(data[1])):
        if data[0][i0][split_var] <= split_point:
            data1[1].append(data[1][i0])
            data1[0].append(data[0][i0])
            data1[2].append(data[2][i0])
        else:
            data2[1].append(data[1][i0])
            data2[0].append(data[0][i0])
            data2[2].append(data[2][i0])

    return [data1, data2]


# 模型计算完毕生成结果文件
# ops_or = file_ops[i]
def output_ops(ops_or):
    tmp = ops_or.split("/")[-1]
    new_ops = "../result/" + tmp[:-4] + "_end.csv"
    return new_ops


# 转化为适应于决策树算法的数据结构
def re_format(data0, target0, mod0):
    train_f0 = []
    train_v0 = []
    train_m0 = []

    test_f0 = []
    test_v0 = []
    test_m0 = []

    index_d = list(data0.index)
    if type(target0) == str:
        for i in range(len(index_d)):
            row_tmp = data0.loc[index_d[i], :]
            value_l = list(row_tmp)
            add0 = value_l[:-2]
            user = index_d[i].split("_")[0]
            train_f0.append(tuple(add0))
            train_v0.append(value_l[-2])
            train_m0.append([user, value_l[-1]])
        train0 = [train_f0, train_v0, train_m0]
        return train0
    elif type(target0) == int:
        # target0 = 1
        for i in range(len(index_d)):
            row_tmp = data0.loc[index_d[i], :]
            test = int(index_d[i].split("_")[1]) % mod0
            user = index_d[i].split("_")[0]
            value_l = list(row_tmp)
            add0 = value_l[:-2]
            if test != target0:
                train_f0.append(tuple(add0))
                train_v0.append(value_l[-2])
                train_m0.append([user, value_l[-1]])
            else:
                test_f0.append(tuple(add0))
                test_v0.append(value_l[-2])
                test_m0.append([user, value_l[-1]])
        train0 = [train_f0, train_v0, train_m0]
        test0 = [test_f0, test_v0, test_m0]
        return train0, test0
    else:
        print("target is wrong!")
        print(target0)
        return None


# 生成标签词典
def find_label(data0):
    # data0 = data_breach
    c_l0 = list(data0.columns)
    dic0 = {}
    for c0 in range(len(c_l0) - 2):
        dic0[c0] = c_l0[c0]
    return dic0


# 生成适合绘图的树结构
# test_json = tree_split(tree0)
# tree0 = tree0.right
def tree_split(tree0):
    if tree0.right is None:
        if tree0.left is None:
            dic0 = [{"children": [], "name": ("%.1f" % tree0.predict)}]
        else:
            dic0 = [{"children": [], "name": tree0.split_lab + ": 是"},
                    {"children": [], "name": tree0.split_lab + ": 否"}]
            # right
            dic0[0]["children"].append({"children": [], "name": ("%.1f" % tree0.predict)})
            # left
            if len(tree_split(tree0.left)) == 1:
                dic0[1]["children"].append(tree_split(tree0.left)[0])
            else:
                dic0[1]["children"].append(tree_split(tree0.left)[0])
                dic0[1]["children"].append(tree_split(tree0.left)[1])
    else:
        if tree0.left is None:
            dic0 = [{"children": [], "name": tree0.split_lab + ": 是"},
                    {"children": [], "name": tree0.split_lab + ": 否"}]
            # right 
            if len(tree_split(tree0.right)) == 1:
                dic0[0]["children"].append(tree_split(tree0.right)[0])
            else:
                dic0[0]["children"].append(tree_split(tree0.right)[0])
                dic0[0]["children"].append(tree_split(tree0.right)[1])
                # left
            dic0[1]["children"].append({"children": [], "name": "%.1f" % tree0.predict})

        else:
            dic0 = [{"children": [], "name": tree0.split_lab + ": 是"},
                    {"children": [], "name": tree0.split_lab + ": 否"}]
            # right 
            if len(tree_split(tree0.right)) == 1:
                dic0[0]["children"].append(tree_split(tree0.right)[0])
            else:
                dic0[0]["children"].append(tree_split(tree0.right)[0])
                dic0[0]["children"].append(tree_split(tree0.right)[1])
                # left
            if len(tree_split(tree0.left)) == 1:
                dic0[1]["children"].append(tree_split(tree0.left)[0])
            else:
                dic0[1]["children"].append(tree_split(tree0.left)[0])
                dic0[1]["children"].append(tree_split(tree0.left)[1])

    return dic0


# 树结构转化为词典
# n_json = tree_to_dic(tree0)
def tree_to_dic(tree0):
    # tree0 = tree_best

    dic0 = [{"children": [], "name": tree0.split_lab}]
    if tree0.get_length() == 1:
        dic0[0]["children"].append({"children": [], "name": "%.1f" % tree0.predict})
    else:
        sub_list0 = tree_split(tree0)
        if len(sub_list0) == 1:
            dic0[0]["children"].append(sub_list0[0])
        else:
            dic0[0]["children"].append(sub_list0[0])
            dic0[0]["children"].append(sub_list0[1])

    return dic0


# 生成适合绘图的树结构，预测值取指数（适用于对数数据处理的模型）
def tree_split_exp(tree0):
    if tree0.right is None:
        if tree0.left is None:
            dic0 = [{"children": [], "name": ("%.1f" % math.exp(tree0.predict))}]
        else:
            dic0 = [{"children": [], "name": tree0.split_lab + ": 是"},
                    {"children": [], "name": tree0.split_lab + ": 否"}]
            # right
            dic0[0]["children"].append({"children": [], "name": ("%.1f" % math.exp(tree0.predict))})
            # left
            if len(tree_split_exp(tree0.left)) == 1:
                dic0[1]["children"].append(tree_split_exp(tree0.left)[0])
            else:
                dic0[1]["children"].append(tree_split_exp(tree0.left)[0])
                dic0[1]["children"].append(tree_split_exp(tree0.left)[1])
    else:
        if tree0.left is None:
            dic0 = [{"children": [], "name": tree0.split_lab + ": 是"},
                    {"children": [], "name": tree0.split_lab + ": 否"}]
            # right 
            if len(tree_split_exp(tree0.right)) == 1:
                dic0[0]["children"].append(tree_split_exp(tree0.right)[0])
            else:
                dic0[0]["children"].append(tree_split_exp(tree0.right)[0])
                dic0[0]["children"].append(tree_split_exp(tree0.right)[1])
                # left
            dic0[1]["children"].append({"children": [], "name": "%.1f" % math.exp(tree0.predict)})

        else:
            dic0 = [{"children": [], "name": tree0.split_lab + ": 是"},
                    {"children": [], "name": tree0.split_lab + ": 否"}]
            # right 
            if len(tree_split_exp(tree0.right)) == 1:
                dic0[0]["children"].append(tree_split_exp(tree0.right)[0])
            else:
                dic0[0]["children"].append(tree_split_exp(tree0.right)[0])
                dic0[0]["children"].append(tree_split_exp(tree0.right)[1])
                # left
            if len(tree_split_exp(tree0.left)) == 1:
                dic0[1]["children"].append(tree_split_exp(tree0.left)[0])
            else:
                dic0[1]["children"].append(tree_split_exp(tree0.left)[0])
                dic0[1]["children"].append(tree_split_exp(tree0.left)[1])

    return dic0


# 树结构转化为词典（指数版本）
# n_json = tree_to_dic(tree0)
def tree_to_dic_exp(tree0):
    # tree0 = tree_best

    dic0 = [{"children": [], "name": tree0.split_lab}]
    if tree0.get_length() == 1:
        dic0[0]["children"].append({"children": [], "name": "%.1f" % math.exp(tree0.predict)})
    else:
        sub_list0 = tree_split_exp(tree0)
        if len(sub_list0) == 1:
            dic0[0]["children"].append(sub_list0[0])
        else:
            dic0[0]["children"].append(sub_list0[0])
            dic0[0]["children"].append(sub_list0[1])

    return dic0


# 绘制树的结构图
def plot_tree(data0, title0, ops0):
    # data0, title0, ops0 = n_json, "test", "./test.html"
    tree_e = plot_tree_by_py()
    tree_e.add("", data0, initial_tree_depth=-1,
               leaves_label_opts=opts.LabelOpts(font_size=9))
    tree_e.set_series_opts(label_opts=opts.LabelOpts(font_size=11)),
    tree_e.set_global_opts(title_opts=opts.TitleOpts(title=title0,
                                                     pos_bottom="0%",
                                                     pos_left="center"))

    if ops0.split(".")[-1] == "html":
        tree_e.render(ops0)
    else:
        make_snapshot(driver, tree_e.render(), ops0)

    return None


# 随机森林算法
class Forest(object):

    def __init__(self, trees):
        self.trees = trees

    def lookup(self, x):
        # x = scale_test_data[0][4]
        # self = forest0
        """Returns the predicted value given the parameters."""
        preds = list(map(lambda t: t.lookup(x), self.trees))
        return numpy.mean(preds)

    def predict_all(self, data):
        """Returns the predicted values for a list of data points."""
        return list(map(lambda x: self.lookup(x), data))


# 生成多个训练集
def make_boot(pairs, n):
    """Construct a bootstrap sample from the data."""
    # numpy.random.choice(5, 3, replace=True, p=[0.1, 0, 0.3, 0.6, 0])
    inds = numpy.random.choice(n, n, replace=True)
    p_1_0 = list(map(lambda x: pairs[0][x], inds))
    p_2_0 = list(map(lambda x: pairs[1][x], inds))
    p_3_0 = list(map(lambda x: pairs[2][x], inds))
    sample0 = [p_1_0, p_2_0, p_3_0]
    return sample0


# 随机森林模型生成
def make_forest(data, b, max_depth, labels, loss_func, fea0):
    """Function to grow a random forest given some training data."""
    trees = []
    n = len(data)
    # pairs = list(data.items())
    pairs = re_format(data, "all", 5)
    # full_tree = grow_tree(data, depth, max_depth, labels, start, loss_func, fea0)
    for b in range(b):
        boot = make_boot(pairs, n)
        trees.append(rp.grow_tree(boot, 0, max_depth, labels, True, loss_func, fea0))

    return Forest(trees)


# GBDT
class GBDT(object):

    def __init__(self, trees):
        self.trees = trees

    def lookup(self, x):
        # x = scale_test_data[0][i]
        # self = forest0
        """Returns the predicted value given the parameters."""
        preds = list(map(lambda t: t.lookup(x), self.trees))
        return max(sum(preds), 0)

    def predict_all(self, data):
        """Returns the predicted values for a list of data points."""
        return list(map(lambda x: self.lookup(x), data))


# 计算残差
def get_res(val0, plu0, learn0):
    # list((value0 - plus_value0) * learn_rate0)
    # val0, plu0, learn0 = value0, plus_value0, learn_rate0
    n_l0 = []
    for i0 in range(len(val0)):
        tmp = max(val0[i0] - plu0[i0], 0) * learn0
        n_l0.append(tmp)
    return n_l0


# 生成GBDT模型
def make_gbdt_tree(data0, tree_num0, learn_rate0, max_depth0,
                   labels0, loss_func0, fea0):
    """
    data0, tree_num0 = breach_train_data, 6
    learn_rate0, max_depth0 = 0.5, 6
    labels0, loss_func0 = labels0, loss_l2
    """
    scale_dat0 = re_format(data0, "all", 5)
    cov0 = scale_dat0[0]
    value0 = np.array(scale_dat0[1])
    user0 = scale_dat0[2]
    initial_tree0 = rp.grow_tree(scale_dat0, 0, max_depth0,
                                 labels0, True, loss_func0, fea0)
    trees = [initial_tree0]
    plus_value0 = np.array(initial_tree0.predict_all(cov0))

    for j in range(tree_num0):
        residuals0 = list((value0 - plus_value0) * learn_rate0)
        new_dat0 = [cov0, residuals0, user0]
        new_tree0 = rp.grow_tree(new_dat0, 0, max_depth0,
                                 labels0, True, loss_func0, fea0)
        new_predict0 = np.array(new_tree0.predict_all(cov0))
        plus_value0 = plus_value0 + new_predict0

        trees.append(new_tree0)

    return GBDT(trees)


# 数据对数处理
def log_data(dat0):
    # dat0 = breach_train_data
    new_rec0 = []
    old_rec0 = list(dat0["数据泄露量"])
    for h0 in old_rec0:
        tmp = math.log(h0)
        if tmp == 0:
            tmp = 0.00000001
        new_rec0.append(tmp)
    dat0.drop("数据泄露量", axis=1, inplace=True)
    dat0["数据泄露量"] = new_rec0
    return dat0


# 数据指数处理
def exp_data(array0):
    # array0 = base_predict0
    new_ar0 = []

    for a0 in list(array0):
        new_ar0.append(math.exp(a0))

    return np.array(new_ar0)


# 主函数
def main_function(picture_path0, dir_path0, fac_num0, 
                  depth0, type0, b_num0, unit0):
    """
    dir_path0, fac_num0, depth0, type0 = dir_path, 5, 6, ".html"
    b_num0, unit0 = 1, 10 ** 16
    picture_path0：图片存储位置
    dir_path0：数据位置
    fac_num0：几折交叉验证
    depth0：最大深度
    type0：图像存储类型
    b_num0：图像标号起始值
    unit0：科学计数法处理
    """

    begin_pic0 = b_num0
    np.random.seed(105)

    file_train_ops = csv_file_ops(dir_path0, "data_train_")
    file_test_ops = csv_file_ops(dir_path0, "data_test_")

    for i in range(len(file_train_ops)):
        save_result_ops = output_ops(file_train_ops[i])
        if os.path.isfile(save_result_ops):
            continue

        cat1, cat2 = ops2info(file_train_ops[i])
        fea0 = False

        dict_info = {}
        train_error = {}

        breach_train_data = pd.read_csv(file_train_ops[i], index_col=0)
        # breach_train_data = log_data(breach_train_data)
        breach_test_data = pd.read_csv(file_test_ops[i], index_col=0)
        # log
        rec_train_or = list(breach_train_data["数据泄露量"])
        breach_train_data["数据泄露量"] = list(map(lambda x: math.log(x), rec_train_or))

        scale_test_data = re_format(breach_test_data, "all", fac_num0)

        dict_info["类别一"] = cat1
        dict_info["类别二"] = cat2
        train_error["类别一"] = cat1
        train_error["类别二"] = cat2

        labels0 = find_label(breach_train_data)

        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("%s: -----Begin!-----" % now_time)
        loss_choose = "L2"
        depth_0 = 1
        print("---Category 1: %s, Category 2: %s. " % (cat1, cat2))
        print(f"---Cross validation: {fac_num0:d}-fold. ")
        print("---Max depth: %d, Loss function: %s" % (depth_0, loss_choose))
        tree_best, train_error0 = rp.cvt(breach_train_data, depth_0, labels0, fac_num0, loss_l2, fea0)
        base_predict0 = np.array(tree_best.predict_all(scale_test_data[0]))
        base_predict0 = exp_data(base_predict0)

        error_base = sum((np.array(scale_test_data[1]) - base_predict0) ** 2)
        dict_info["基准"] = [error_base / unit0]
        train_error["基准"] = [train_error0 / unit0]
        print("---error: %f. " % (error_base / unit0))
        # tree_json_or = tree_to_dic(tree_best)
        tree_json = tree_to_dic_exp(tree_best)

        title_pic = "图片" + str(begin_pic0) + "：" + cat1 + "和" + cat2
        title_pic = title_pic + "基于L2损失 (最大深度=1) 的决策树模型 (基准模型)"
        save_ops = picture_path0 + title_pic + type0
        plot_tree(tree_json, title_pic, save_ops)
        begin_pic0 += 1
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("%s: -----End!-----\n" % now_time)

        # 损失函数的调用词典
        function_dic0 = {"L2": loss_l2, "非齐次I类": loss_415, "非齐次II类": loss_416, "齐次I类": loss_419, "齐次II类": loss_420}

        for func0 in function_dic0.keys():
            loss_choose = func0
            loss_func0 = function_dic0[func0]
            '''
            loss_choose = "L2"
            loss_func0 = function_dic0[loss_choose]  
            '''
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("%s: -----Begin!-----" % now_time)
            print("---Category 1: %s, Category 2: %s. " % (cat1, cat2))
            print("\n---CART: Cross validation: %d-fold. " % fac_num0)
            print("---Max depth: %d, Loss function: %s" % (depth0, loss_choose))
            tree_best, train_error0 = rp.cvt(breach_train_data, depth0, labels0, fac_num0, loss_func0, fea0)
            cart_predict0 = np.array(tree_best.predict_all(scale_test_data[0]))
            cart_predict0 = exp_data(cart_predict0)

            error_cart0 = sum((np.array(scale_test_data[1]) - cart_predict0) ** 2)
            dict_info["CART-" + loss_choose] = [error_cart0 / unit0]
            train_error["CART-" + loss_choose] = [train_error0 / unit0]
            rpe_cart0 = error_cart0 / error_base
            print("---error: %f, rpe: %f. " % (error_cart0 / unit0, rpe_cart0))
            tree_json = tree_to_dic_exp(tree_best)
            title_pic = "图片" + str(begin_pic0) + "：" + cat1 + "和" + cat2
            title_pic = title_pic + "基于" + loss_choose + "损失的决策树模型"
            save_ops = picture_path0 + title_pic + type0
            plot_tree(tree_json, title_pic, save_ops)
            begin_pic0 += 1
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("%s: -----End!-----\n" % now_time)

        for func1 in function_dic0.keys():
            loss_choose = func1
            loss_func0 = function_dic0[func1]

            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("%s: -----Begin!-----" % now_time)
            tree_num_forest0 = 100
            fea_forest_0 = True  # bagging
            depth_forest0 = 6
            print("---Category 1: %s, Category 2: %s. " % (cat1, cat2))
            print("\n---Random forest: number of tree: %d, bagging: %s. " % (tree_num_forest0,
                                                                             str(fea_forest_0)))
            print("---Max depth: %d, Loss function: %s" % (depth_forest0, loss_choose))

            forest0 = make_forest(breach_train_data, tree_num_forest0, depth_forest0,
                                  labels0, loss_func0, fea_forest_0)
            forest_predict0 = np.array(forest0.predict_all(scale_test_data[0]))
            forest_predict0 = exp_data(forest_predict0)

            error_forest0 = sum((np.array(scale_test_data[1]) - forest_predict0) ** 2)
            rpe_forest = error_forest0 / error_base
            dict_info["随机森林-" + loss_choose] = [error_forest0 / unit0]
            print("---error: %f, rpe: %f. " % (error_forest0 / unit0, rpe_forest))
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("%s: -----End!-----\n" % now_time)

        for func2 in function_dic0.keys():
            loss_choose = func2
            loss_func0 = function_dic0[func2]

            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("%s: -----Begin!-----" % now_time)
            tree_num_gbdt0 = 100
            fea_gbdt_0 = False  # bagging
            depth_gbdt0 = 6
            learn_rate_gbdt0 = 1
            print("---Category 1: %s, Category 2: %s. " % (cat1, cat2))
            print("\n---GBDT: number of tree: %d, learn rate: %f. " % (tree_num_gbdt0,
                                                                       learn_rate_gbdt0))
            print("---Max depth: %d, Loss function: %s" % (depth_gbdt0, loss_choose))

            gbdt_tree0 = make_gbdt_tree(breach_train_data, tree_num_gbdt0,
                                        learn_rate_gbdt0, depth_gbdt0,
                                        labels0, loss_func0, fea_gbdt_0)
            gbdt_predict0 = np.array(gbdt_tree0.predict_all(scale_test_data[0]))
            gbdt_predict0 = exp_data(gbdt_predict0)

            error_gbdt = sum((np.array(scale_test_data[1]) - gbdt_predict0) ** 2)
            rpe_gbdt = error_gbdt / error_base
            dict_info["GBDT-" + loss_choose] = [error_gbdt / unit0]
            print("---error: %f, rpe: %f. " % (error_gbdt / unit0, rpe_gbdt))
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("%s: -----End!-----\n" % now_time)

        df_final = pd.DataFrame.from_dict(dict_info)
        # pd_final = pd.concat([df1, rule_rpe_df], axis=1)
        df_final.to_csv(save_result_ops, index=None, encoding='utf_8_sig')

    return None


# =============================== the main function ===========================
if __name__ == '__main__':
    
    data_path = "../data/"
    picture_path = "../RTC_picture/"
    main_function(picture_path, data_path, 5, 6, ".html", 1, 10 ** 16)
