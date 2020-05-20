# -*- coding: utf-8 -*-
"""
Created on Wed May 29 09:22:55 2019

@author: Zhaoke

文件说明：代码实现Diao等人的决策树信度模型

参考代码：
https://github.com/chandarb/Python-Regression-Tree-Forest
参考文献：
Diao L, Weng C. Regression Tree Credibility Model[J]. 
The North American Actuarial Journal, 2019, 23(2): 169-196.
"""

import numpy
import copy
from bisect import bisect_right
import random


# 建立树对象
class Tree(object):

    # 初始化树属性
    def __init__(self, error, predict, start, num_points):
        self.error = error
        self.predict = predict
        self.start = start
        self.split_var = None
        self.split_val = None
        self.split_lab = None
        self.left = None
        self.right = None
        self.num_points = num_points

    # 给定一条自变量（协变量）信息，返回一个对应的预测值
    def lookup(self, x):
        if self.left is None:
            return self.predict
        if x[self.split_var] <= self.split_val:
            return self.left.lookup(x)
        return self.right.lookup(x)

    # 给定多条自变量（协变量）信息，返回多个预测值
    def predict_all(self, data):
        return list(map(lambda x: self.lookup(x), data))

    # 寻找alpha的最小值和第一个不能最小化代价复杂度函数值的（树枝）子树
    def find_weakest(self):
        if self.right is None:
            return float("Inf"), [self]
        b_error, num_nodes = self.get_cost_params()
        alpha = (self.error - b_error) / (num_nodes - 1)
        alpha_right, tree_right = self.right.find_weakest()
        alpha_left, tree_left = self.left.find_weakest()
        smallest_alpha = min(alpha, alpha_right, alpha_left)
        smallest_trees = []

        # 如果有多个弱连接树，则全部折叠（剪枝）
        if smallest_alpha == alpha:
            smallest_trees.append(self)
        if smallest_alpha == alpha_right:
            smallest_trees = smallest_trees + tree_right
        if smallest_alpha == alpha_left:
            smallest_trees = smallest_trees + tree_left
        return smallest_alpha, smallest_trees

    # 获得一系列的alpha值和其对应的一系列嵌套子树后，选取最优树及其alpha值
    @property
    def prune_tree(self):
        trees = [copy.deepcopy(self)]
        alphas = [0]
        new_tree = copy.deepcopy(self)
        while 1:
            alpha, nodes = new_tree.find_weakest()
            for node in nodes:
                node.right = None
                node.left = None
            trees.append(copy.deepcopy(new_tree))
            alphas.append(alpha)
            if nodes[-1].start:
                break
        return alphas, trees

    # 返回损失值（误差）和子节点个数
    def get_cost_params(self):
        if self.right is None:
            return self.error, 1
        error, num_nodes = self.right.get_cost_params()
        left_error, left_num = self.left.get_cost_params()
        error += left_error
        num_nodes += left_num
        # error of left and right node
        # error of all subtree
        return error, num_nodes

    # 返回树的深度
    def get_length(self):
        if self.right is None:
            return 1
        right_len = self.right.get_length()
        left_len = self.left.get_length()
        return max(right_len, left_len) + 1

    # 对数据依据协变量及其取值进行划分
    def depart_dat(self, data):

        split_point, split_var = self.split_val, self.split_var
        # left
        data1 = [[], [], []]
        # right
        data2 = [[], [], []]

        for i in range(len(data[1])):
            if data[0][i][split_var] <= split_point:
                data1[1].append(data[1][i])
                data1[0].append(data[0][i])
                data1[2].append(data[2][i])
            else:
                data2[1].append(data[1][i])
                data2[0].append(data[0][i])
                data2[2].append(data[2][i])

        return data1, data2

    def to_part(self, data0):
        data_set0 = []
        self.__separate(data0, data_set0)

        return data_set0

    def __separate(self, data0, data_set0):

        if self.right is None:
            data_set0.append(data0)
            return

        dat_l, dat_r = self.depart_dat(data0)

        # tree_best.right
        self.right.__separate(dat_r, data_set0)
        # tree_best.left
        self.left.__separate(dat_l, data_set0)
        return


# 树的生长
def grow_tree(data, depth, max_depth, labels, start, loss_func, feature_bag0):
    data_value = data[1]
    data_key = data[0]
    n_min_tmp = cal_Nmin(data)

    root = Tree(loss_func(data), numpy.mean(data_value), start, len(data_value))

    # 防止结构参数为0
    if n_min_tmp <= 2:
        return root

    # 树的最大深度
    if depth >= max_depth:
        return root
    num_vars = len(data_key[0])

    min_error = -1
    min_split = -1
    split_var = -1

    # 特征（各项协变量）随机抽取，抽取总特征的1/2次方个特征
    if feature_bag0:
        cand_vars = random.sample(range(num_vars), int(num_vars ** 0.5))
    else:
        cand_vars = range(num_vars)

    # 按特征分区
    for i in cand_vars:
        var_space = [x[i] for x in data[0]]
        if min(var_space) == max(var_space):
            continue
        else:
            # 由于协变量都是0-1的分类变量，所以以0.5为划分数值
            split = 0.5
            # 计算损失（误差）
            error = error_function(split, i, data, loss_func)
            # 选择具有最小化误差的参数
            if (error < min_error) or (min_error == -1):
                min_error = error
                min_split = split
                split_var = i

    # 不需要再划分
    if split_var == -1:
        return root

    root.split_var = split_var
    root.split_val = min_split
    if split_var in labels:
        root.split_lab = labels[split_var]

    # 按照损失最小化参数进行分区
    data1 = [[], [], []]
    data2 = [[], [], []]
    for i in range(len(data[0])):
        if data[0][i][split_var] <= min_split:
            data1[1].append(data[1][i])
            data1[0].append(data[0][i])
            data1[2].append(data[2][i])
        else:
            data2[1].append(data[1][i])
            data2[0].append(data[0][i])
            data2[2].append(data[2][i])

    # 生成左子树和右子树
    root.left = grow_tree(data1, depth + 1, max_depth, labels, False, loss_func, feature_bag0)
    root.right = grow_tree(data2, depth + 1, max_depth, labels, False, loss_func, feature_bag0)

    return root


def cvt(data_or, max_depth, labels, fac_num0, loss_func, fea0):
    '''
    data_or：数据集
    max_depth：最大深度
    labels：协变量标签
    fac_num0：交叉验证为几折
    loss_func：损失函数
    fea0：是否进行特征抽取
    '''    
    # 初始化 形成符合算法的数据结构
    data = re_format(data_or, "all", fac_num0)
    # 树的生长
    full_tree = grow_tree(data, 0, max_depth, labels, True, loss_func, fea0)
    # full_a_or, full_t_or：一系列alpha和相应的树
    full_a_or, full_t_or = full_tree.prune_tree
    full_a = []
    full_t = []
    for f_a0 in range(len(full_a_or)):
        if full_a_or[f_a0] < float("Inf"):
            full_a.append(full_a_or[f_a0])
            full_t.append(full_t_or[f_a0])

    a_s = []
    for i in range(len(full_a) - 1):
        a_s.append(abs(full_a[i] * full_a[i + 1]) ** 0.5)
    a_s.append(full_a[-1])

    # 每个训练集对应最优树
    t_vs = []
    # 每个训练集对应的测试集
    test_vs = []
    # 每个训练集的最优树对应的alpha值
    alpha_vs = []

    # 训练集上树的生长以及剪枝
    fac_l = range(fac_num0)
    for i in fac_l:
        # 划分训练集和测试集，数据标号方法，见《Regression Tree Credibility Model》
        train, test = re_format(data_or, int(i), fac_num0)
        full_tree_v = grow_tree(train, 0, max_depth,
                                labels, True, loss_func, fea0)
        alphas_v, trees_v = full_tree_v.prune_tree
        t_vs.append(trees_v)
        alpha_vs.append(alphas_v)
        test_vs.append(test)

    # 选择交叉验证误差最小的树 
    min_r = float("Inf")
    min_ind = 0
    for i in range(len(full_t)):
        ak = a_s[i]
        r_k = 0
        for j in range(len(test_vs)):
            # 
            a_vs = alpha_vs[j]
            tr_vs = t_vs[j]
            alph_ind = bisect_right(a_vs, ak) - 1
            para = test_vs[j][0]
            va = test_vs[j][1]
            pred_vals = Tree.predict_all(tr_vs[alph_ind], para)
            r_kv = numpy.sum((numpy.array(va) - numpy.array(pred_vals)) ** 2)
            r_k = r_k + r_kv
        if r_k < min_r:
            min_r = r_k
            min_ind = i
    return full_t[min_ind], min_r


# 计算划分后，在两个分区上的损失之和
def error_function(split_point, split_var, data, loss_func):
    data1 = [[], [], []]
    data2 = [[], [], []]
    for i in range(len(data[1])):
        if data[0][i][split_var] <= split_point:
            data1[1].append(data[1][i])
            data1[0].append(data[0][i])
            data1[2].append(data[2][i])
        else:
            data2[1].append(data[1][i])
            data2[0].append(data[0][i])
            data2[2].append(data[2][i])

    return loss_func(data1) + loss_func(data2)


# 划分训练集 测试集
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


# 计算最小记录数，防止结构参数为0
def cal_Nmin(sc_dat):
    mi_l = []
    mi = 1
    for u in range(len(sc_dat[2]) - 1):
        if sc_dat[2][u + 1][0] == sc_dat[2][u][0]:
            mi += 1
        else:
            mi_l.append(mi)
            mi = 1
    mi_l.append(mi)

    return min(mi_l)
