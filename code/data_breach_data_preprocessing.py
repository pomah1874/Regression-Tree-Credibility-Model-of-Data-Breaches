# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 08:40:57 2020

@author: Zhaoke

文件说明：划分为14个适应于决策树信度模型的数据集

相关数据预处理需结合 data_breach_picture.py 来看

数据源：https://github.com/vz-risk/vcdb
"""

import pandas as pd
import numpy as np

# 英汉翻译词典
tran_dic = {"victim.employee_count": "雇员数量", "victim.employee_count.1 to 10": "雇员数量: 1-10",
            "victim.employee_count.10001 to 25000": "雇员数量: 10001-25000",
            "victim.employee_count.1001 to 10000": "雇员数量: 1001-10000",
            "victim.employee_count.101 to 1000": "雇员数量: 101-1000", "victim.employee_count.11 to 100": "雇员数量: 11-100",
            "victim.employee_count.25001 to 50000": "雇员数量: 25001-50000",
            "victim.employee_count.50001 to 100000": "雇员数量: 50001-100000",
            "victim.employee_count.Over 100000": "雇员数量: 100000-Inf", "timeline.incident.year": "事件发生年份",
            "year.2010": "年份: 2010", "year.2011": "年份: 2011", "year.2012": "年份: 2012", "year.2013": "年份: 2013",
            "year.2014": "年份: 2014", "year.2015": "年份: 2015", "year.2016": "年份: 2016", "year.2017": "年份: 2017",
            "year.2018": "年份: 2018", "year.2019": "年份: 2019", "actor": "威胁者", "actor.External": "威胁者: 外部人员",
            "actor.Internal": "威胁者: 内部人员", "actor.Partner": "威胁者: 合作伙伴", "actor.Multiple": "威胁者: 多方势力",
            "action": "威胁行为", "action.Error": "威胁行为: 错误行为", "action.Hacking": "威胁行为: 黑客袭击",
            "action.Misuse": "威胁行为: 不当使用", "action.Physical": "威胁行为: 物理操作", "action.Malware": "威胁行为: 恶意软件",
            "action.Social": "威胁行为: 社交策略", "pattern": "威胁模式", "pattern.Point of Sale": "威胁模式: 销售点",
            "pattern.Crimeware": "威胁模式: 犯罪软件", "pattern.Payment Card Skimmers": "威胁模式: 支付卡读取器",
            "pattern.Cyber-Espionage": "威胁模式: 网络间谍", "pattern.Lost and Stolen Assets": "威胁模式: 遗失及被盗资产",
            "pattern.Web Applications": "威胁模式: 网络应用程序", "pattern.Privilege Misuse": "威胁模式: 特权滥用",
            "pattern.Miscellaneous Errors": "威胁模式: 各种错误", "pattern.Denial of Service": "威胁模式: 系统服务中断",
            "asset.variety": "受威胁资产", "asset.variety.Server": "受威胁资产: 服务器", "asset.variety.Kiosk/Term": "受威胁资产: 自助服务终端",
            "asset.variety.User Dev": "受威胁资产: 用户设备", "asset.variety.Media": "受威胁资产: 媒介",
            "asset.variety.Person": "受威胁资产: 人员", "asset.variety.Network": "受威胁资产: 网络",
            "asset.variety.Embedded": "受威胁资产: 嵌入式设备", "actor.motive": "威胁动机", "actor.motive.Convenience": "动机: 方便的权宜之计",
            "actor.motive.Espionage": "动机: 间谍活动或竞争优势", "actor.motive.Fear": "动机: 恐惧或胁迫",
            "actor.motive.Financial": "动机: 经济或个人利益", "actor.motive.Fun": "动机: 有趣、好奇或自豪",
            "actor.motive.Grudge": "动机: 怨恨或个人冒犯", "actor.motive.Ideology": "动机: 意识形态或抗议", "actor.motive.NA": "动机: 无意之举",
            "actor.motive.Secondary": "动机: 协助发动另一场攻击", "actor.motive.Other": "动机: 其他", "victim.industry.name": "受威胁行业",
            "victim.industry.name.Healthcare": "行业: 医疗行业", "victim.industry.name.Public": "行业: 公共部门",
            "victim.industry.name.Finance": "行业: 金融行业", "victim.industry.name.Information": "行业: 信息行业",
            "victim.industry.name.Educational": "行业: 教育行业", "victim.industry.name.Retail": "行业: 零售业",
            "victim.industry.name.Professional": "行业: 专业服务", "victim.industry.name.Other Services": "行业: 其他服务行业",
            "victim.industry.name.Manufacturing": "行业: 制造业", "victim.industry.name.Administrative": "行业: 行政管理",
            "victim.industry.name.Accomodation": "行业: 住宿行业", "victim.industry.name.Transportation": "行业: 交通行业",
            "victim.industry.name.Trade": "行业: 商业", "victim.industry.name.Entertainment": "行业: 娱乐行业",
            "victim.industry.name.Real Estate": "行业: 房地产", "victim.industry.name.Utilities": "行业: 公共事业",
            "victim.industry.name.Construction": "行业: 建筑行业", "victim.industry.name.Mining": "行业: 矿业",
            "victim.industry.name.Management": "行业: 管理行业", "victim.industry.name.Agriculture": "行业: 农业",
            "attribute.confidentiality.data_total": "数据泄露量"}


# 删除空值
def data_nan_filter(data0, col_name0):
    # data0 = data_breach
    # col_name0 = "attribute.confidentiality.data_total"
    index_l0 = []
    for i0 in data0.index:
        if not pd.isna(data0.loc[i0, col_name0]):
            index_l0.append(i0)
    df0 = data0.loc[index_l0, ]
    diff0 = data0.shape[0] - df0.shape[0]
    print("原数据量：%d, 去除空值后, 新数据量：%d, 数据损失：%d. " % (data0.shape[0],
                                                  df0.shape[0], diff0))
    return df0


# 删除未知值
def drop_unknown(data0, form_str0):
    # data0 = data_breach
    # form_str0 = "victim.country."
    n_n0 = form_str0 + "Unknown"
    dat_new0 = data0[((data0[n_n0] == False) | (data0[n_n0] == "FALSE"))]
    diff0 = data0.shape[0] - dat_new0.shape[0]
    print("原数据量：%d, 去除未知项后, 新数据量：%d, 数据损失：%d. " % (data0.shape[0],
                                                   dat_new0.shape[0], diff0))
    return dat_new0


# 删除未知值
def drop_unknown_direc(data0, col_name0):
    # data0 = data_breach
    # col_name0 = "Actor"
    dat_new0 = data0[((data0[col_name0] != False) & (data0[col_name0] != "FALSE"))]
    diff0 = data0.shape[0] - dat_new0.shape[0]
    print("原数据量：%d, 去除未知项后, 新数据量：%d, 数据损失：%d. " % (data0.shape[0],
                                                   dat_new0.shape[0], diff0))
    return dat_new0


# 选取部分变量名
def search_country(data0, form_str0):
    # data0 = data_breach
    # form_str0 = "asset.variety."
    # form_str0 = "asset.assets.variety."
    # form_str0 = "victim.country."
    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if form_str0 in it0:
            col_name_list0.append(it0)

    return col_name_list0


# 泄漏事件随年份变化的统计结果
def sta_country_over_time(year0, data0, limit0):
    # year0, data0, limit0 = year_list, data_breach, 4
    col_cou0 = search_country(data0, "victim.country.")
    user_l0 = {}
    in_num = 0
    country_test0 = []
    for cou0 in col_cou0:
        # user_l0[cou0] = {}
        # cou0 = 'victim.country.CN'
        cou_tmp = {}
        dat_tmp = data0[(data0[cou0] == True) | (data0[cou0] == "TRUE") |
                        (data0[cou0] == 1)]
        # add0年有事件
        # add0年共经历事件num_tmp
        add0 = 0
        num_tmp = 0
        for y0 in year0:
            num0 = dat_tmp[(dat_tmp['timeline.incident.year'] == int(y0)) |
                           (dat_tmp['timeline.incident.year'] == y0)].shape[0]
            if num0 > 0:
                add0 += 1
            cou_tmp[y0] = num0
            num_tmp += num0
        if add0 > 0:
            user_l0[cou0] = cou_tmp
            in_num += num_tmp
            if num_tmp > limit0:
                country_test0.append(cou0)

    diff0 = data0.shape[0] - in_num
    print("\n原数据量：%d, 年份：%s-%s, 数据损失：%d, 覆盖事件：%d, 覆盖国家：%d, 事件总数大于 %d 的国家有 %d 个. \n" % (
        data0.shape[0], year0[0], year0[-1], diff0, in_num, len(user_l0), limit0, len(country_test0)))

    '''
    运行结果展示：
    原数据量：3211, 年份：2019-2005, 数据损失：22, 覆盖事件：3189, 覆盖国家：73, 事件总数大于 4 的国家有 25 个.
    原数据量：3211, 年份：2019-2006, 数据损失：34, 覆盖事件：3177, 覆盖国家：73, 事件总数大于 4 的国家有 25 个.
    原数据量：3211, 年份：2019-2007, 数据损失：42, 覆盖事件：3169, 覆盖国家：73, 事件总数大于 4 的国家有 24 个.
    原数据量：3211, 年份：2019-2008, 数据损失：62, 覆盖事件：3149, 覆盖国家：73, 事件总数大于 4 的国家有 24 个. 
    原数据量：3211, 年份：2019-2009, 数据损失：96, 覆盖事件：3115, 覆盖国家：73, 事件总数大于 4 的国家有 24 个. 
    原数据量：3211, 年份：2019-2010, 数据损失：126, 覆盖事件：3085, 覆盖国家：73, 事件总数大于 4 的国家有 24 个. 
    原数据量：3211, 年份：2019-2011, 数据损失：296, 覆盖事件：2915, 覆盖国家：73, 事件总数大于 4 的国家有 24 个.    
    原数据量：3211, 年份：2019-2012, 数据损失：561, 覆盖事件：2650, 覆盖国家：73, 事件总数大于 4 的国家有 23 个.    
    原数据量：3211, 年份：2019-2013, 数据损失：1055, 覆盖事件：2156, 覆盖国家：64, 事件总数大于 4 的国家有 20 个.
    原数据量：3211, 年份：2019-2014, 数据损失：1672, 覆盖事件：1539, 覆盖国家：54, 事件总数大于 4 的国家有 16 个. 
    原数据量：3211, 年份：2019-2015, 数据损失：2050, 覆盖事件：1161, 覆盖国家：52, 事件总数大于 4 的国家有 13 个.    
    原数据量：3211, 年份：2019-2016, 数据损失：2473, 覆盖事件：738, 覆盖国家：49, 事件总数大于 4 的国家有 10 个.     
    原数据量：3211, 年份：2019-2017, 数据损失：2803, 覆盖事件：408, 覆盖国家：41, 事件总数大于 4 的国家有 8 个. 
    原数据量：3211, 年份：2019-2018, 数据损失：3006, 覆盖事件：205, 覆盖国家：33, 事件总数大于 4 的国家有 7 个. 
    原数据量：3211, 年份：2019-2019, 数据损失：3134, 覆盖事件：77, 覆盖国家：24, 事件总数大于 4 的国家有 1 个.     
    '''
    return user_l0, country_test0


# 获得变量取值
def search_employ(data0, form_str0):
    # data0 = data_breach
    # form_str0 = "asset.variety."
    # form_str0 = "asset.assets.variety."
    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if form_str0 in it0:
            jump0 = it0.split(".")[-1]
            if (jump0 != "Large") and (jump0 != "Small") and (jump0 != "Unknown"):
                col_name_list0.append(it0)

    return col_name_list0


# 获得变量取值
def search_motive_sub(data0):
    # data0 = data_breach
    sub_dic0 = {}
    colname0 = list(data0.columns)
    for it0 in colname0:
        if ("actor." in it0) and (".motive." in it0):
            tmp_cat0 = it0.split(".")[1]
            tmp_sub0 = it0.split(".")[-1]
            if tmp_sub0 != "Unknown":
                if tmp_sub0 not in sub_dic0.keys():
                    sub_dic0[tmp_sub0] = [tmp_cat0]
                else:
                    sub_dic0[tmp_sub0].append(tmp_cat0)
    return list(sub_dic0.keys())


# 获取动机数据集
def motive_sub_df(sub_list0, data0):
    # data0 = data_breach
    # sub_list0 = sub_motive_name0

    search0 = ["actor.internal.motive.", "actor.external.motive.",
               "actor.partner.motive."]

    new_f0 = "actor.motive."
    dic_sub0 = {}
    for dic0 in sub_list0:
        dic_sub0[new_f0 + dic0] = []

    for index0 in list(data0.index):
        for m0 in sub_list0:
            tmp_tf0 = False
            for name0 in search0:
                if (data0.loc[index0, name0 + m0] == True) or (data0.loc[index0, name0 + m0] == "TRUE"):
                    tmp_tf0 = True
                else:
                    continue
            dic_sub0[new_f0 + m0].append(tmp_tf0)

    motive_df0 = pd.DataFrame.from_dict(dic_sub0)

    return motive_df0


# 获得变量取值
def search_action(data0, form_str0):
    # data0 = data_breach
    # form_str0 = "asset.variety."
    # form_str0 = "action."
    # form_str0 = "actor."
    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if it0.count(".") == 1:
            if it0.split(".")[0] == form_str0:
                # pattern Everything Else
                if (it0.split(".")[-1] != "Unknown") and (
                        it0.split(".")[-1] != "Environmental") and (
                        it0.split(".")[-1] != "Everything Else") and (
                        it0.split(".")[-1] != "Multiple"):
                    col_name_list0.append(it0)

    return col_name_list0


# 获得变量取值
def search_asset(data0, form_str0):
    # data0 = data_breach

    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if form_str0 in it0:
            if it0.split(".")[-1] != "Unknown":
                col_name_list0.append(it0)

    return col_name_list0


# True-False 转化为0-1
def tf_to_num(data0):
    # data0 = data_part1_0
    # data0 = new_df0
    wrong = {}
    w_type = []
    new_df0 = {}
    index_list0 = list(data0.index)
    for col_n0 in data0.columns:
        tmp_list = list(data0[col_n0])
        num_list0 = []
        wrong[col_n0] = []
        for l0 in range(len(tmp_list)):
            if type(tmp_list[l0]) == str:
                if (tmp_list[l0] == "FALSE") or (tmp_list[l0] == "0"):
                    num_list0.append(0)
                elif (tmp_list[l0] == "TRUE") or (tmp_list[l0] == "1"):
                    num_list0.append(1)
                else:
                    wrong[col_n0].append(tmp_list[l0])
                    num_list0.append(tmp_list[l0])
                    if l0 not in w_type:
                        w_type.append(l0)
            elif type(tmp_list[l0]) == bool:
                num_list0.append(tmp_list[l0] + 0)
            elif type(tmp_list[l0]) == int:
                num_list0.append(tmp_list[l0])
            elif type(tmp_list[l0]) == float:
                if pd.isna(tmp_list[l0]):
                    if l0 not in w_type:
                        w_type.append(l0)
                    num_list0.append(tmp_list[l0])
                else:
                    num_list0.append(int(tmp_list[l0]))
            else:
                wrong[col_n0].append(tmp_list[l0])
                num_list0.append(tmp_list[l0])
                if l0 not in w_type:
                    w_type.append(l0)
        new_df0[col_n0] = num_list0

    new_df_from_dic0 = pd.DataFrame.from_dict(new_df0)
    new_df_from_dic0.drop(index=w_type, axis=0, inplace=True)
    n_w_type = []
    for w0 in w_type:
        n_w_type.append(index_list0[w0])
    new_df_from_dic0.index = range(new_df_from_dic0.shape[0])

    return new_df_from_dic0, n_w_type


# 数据处理
def data_breach_deal(year_l0, data0, g_ops0, title0):
    """
    year_l0 = year_list
    data0 = data_breach_or
    g_ops0 = global_ops
    title0 = "all_breach_cart.csv"
    """
    data_total_col0 = "attribute.confidentiality.data_total"
    data_breach0 = data_nan_filter(data0, data_total_col0)
    data_breach0 = drop_unknown(data_breach0, "victim.country.")

    country_time_dic0, country_test_set0 = sta_country_over_time(year_l0,
                                                                 data_breach0, 4)
    country_list0 = list(country_time_dic0.keys())

    employ_cat0 = search_employ(data_breach0, "victim.employee_count.")
    actor_cat0 = search_action(data_breach0, "actor")
    action_cat0 = search_action(data_breach0, "action")
    pattern_cat0 = search_action(data_breach0, "pattern")
    asset_cat0 = search_asset(data_breach0, "asset.variety.")
    data_cat0 = search_asset(data_breach0,
                             "attribute.confidentiality.data.variety.")

    part1_name0 = employ_cat0 + actor_cat0 + action_cat0
    part1_name0 = part1_name0 + pattern_cat0 + asset_cat0 + data_cat0
    part1_name0 = part1_name0 + country_list0
    data_part1_0 = data_breach0[part1_name0]
    data_part1_0, drop_index0 = tf_to_num(data_part1_0)

    data_breach0.drop(index=drop_index0, axis=0, inplace=True)
    '''
    year_dat0 = pd.get_dummies(data_breach0['timeline.incident.year'], 
                                   prefix = '', 
                                   prefix_sep = '', dummy_na = True)
    year_dat0.columns
    '''
    part3_name0 = [data_total_col0, 'timeline.incident.year']
    data_part3_0 = data_breach0[part3_name0]
    data_part3_0.index = range(data_part3_0.shape[0])
    data_part1_0 = pd.concat([data_part1_0, data_part3_0], axis=1)

    # add to data0 
    sub_motive_name0 = search_motive_sub(data_breach0)
    sub_motive_dat0 = motive_sub_df(sub_motive_name0, data_breach0)
    sub_motive_cat0 = list(sub_motive_dat0.columns)
    sub_motive_dat0[sub_motive_cat0] = sub_motive_dat0[sub_motive_cat0].astype('int')

    industry_dat0 = pd.get_dummies(data_breach0['victim.industry.name'],
                                   prefix="victim.industry.name",
                                   prefix_sep='.', dummy_na=True)
    industry_cat0 = []
    for in0 in list(industry_dat0.columns):
        if (in0.split(".")[-1] != "nan") and (in0.split(".")[-1] != "Unknown") and (
                in0.split(".")[-1] != "483") and (in0.split(".")[-1] != "FALSE"):
            industry_cat0.append(in0)
    industry_dat0 = industry_dat0[industry_cat0]
    industry_dat0.index = range(industry_dat0.shape[0])

    # part2_name0 = sub_motive_cat0 + industry_cat0
    data_part2_0 = pd.concat([sub_motive_dat0, industry_dat0], axis=1)

    # all_data_name0 = part1_name0 + part2_name0
    all_data0 = pd.concat([data_part1_0, data_part2_0], axis=1)
    # industry_dat0[industry_cat0] = industry_dat0[industry_cat0].astype('bool')

    all_data0.to_csv(g_ops0 + title0, index=None)

    return all_data0


# 获取变量名称及其子类名称
def name_cat(data0):
    col0 = list(data0.columns)
    n_dic0 = {}
    cov_n0 = []
    for c0 in col0:
        tmp_l0 = c0.split(".")
        if ("data_total" not in c0) and ("timeline.incident.year" not in c0):
            if "country" not in c0:
                cov_n0.append(c0)
            high_cat0 = c0[:-len(tmp_l0[-1])]
            if high_cat0 not in n_dic0.keys():
                n_dic0[high_cat0] = [tmp_l0[-1]]
            else:
                n_dic0[high_cat0].append(tmp_l0[-1])

    cov_n0.append("attribute.confidentiality.data_total")

    return cov_n0, n_dic0


# 获取大类名称
def search_high_cat(dic0, cat_l0):
    # cat_l0 = ['actor.', 'action.', 'asset.variety.']
    # dic0 = name_dic
    out_l0 = []
    if "all" in cat_l0:
        tmp_name_l0 = list(dic0.keys())
        for n_0 in tmp_name_l0:
            if ("year" not in n_0) and ("country" not in n_0):
                tmp_value0 = dic0[n_0]
                for h0 in tmp_value0:
                    out_l0.append(n_0 + h0)
        out_l0.append("attribute.confidentiality.data_total")
        return out_l0

    for c0 in cat_l0:
        tmp_l0 = dic0[c0]
        for l0 in tmp_l0:
            out_l0.append(c0 + l0)
    out_l0.append("attribute.confidentiality.data_total")

    return out_l0


# 转化为符合决策树信度模型要求的数据集
def to_cart_data(data0, country0, cart_n0):
    """
    data0, country0 = data_breach, country_name
    cart_n0 = test_name_list
    """
    in_num = 0
    test_num = 0
    # min incident: 3
    limit0 = 2
    # cat num
    num_all0 = 0
    all_cou_dic = {}
    for cou0 in country0:
        c_n0 = cou0.split(".")[-1]
        df_cou0 = data0[data0[cou0] == 1]
        df_cou0 = df_cou0[cart_n0]
        index0 = df_cou0.index
        c_dic0 = {}
        str_chage0 = {}
        for i0 in index0:
            inc0 = list(df_cou0.loc[i0, :])
            cov_str0 = str(inc0[:-2] + [inc0[-1]])
            if cov_str0 not in str_chage0.keys():
                str_chage0[cov_str0] = inc0[:-2] + [inc0[-1]]
            if cov_str0 not in c_dic0.keys():
                c_dic0[cov_str0] = [inc0[-2]]
            else:
                c_dic0[cov_str0].append(inc0[-2])
        n_dic0 = {}
        label0 = 1
        cou_inc0 = 0
        for str0 in c_dic0.keys():
            l0 = c_dic0[str0]
            cov0 = str_chage0[str0]
            if len(l0) != 1:
                n_l0 = c_n0 + "_" + str(label0)
                label0 += 1
                cou_inc0 += len(l0)
                ave0 = round(float(sum(l0)) / len(l0), 2)
                cov0.append(ave0)
                cov0.append(len(l0))
                n_dic0[n_l0] = cov0
            else:
                if l0[0] > 0:
                    n_l0 = c_n0 + "_" + str(label0)
                    label0 += 1
                    cou_inc0 += len(l0)
                    cov0.append(l0[0])
                    cov0.append(len(l0))
                    n_dic0[n_l0] = cov0
                else:
                    continue

        if len(n_dic0.keys()) > limit0:
            num_all0 += len(n_dic0.keys())
            test_num += 1
            in_num += cou_inc0
            all_cou_dic[c_n0] = n_dic0

    diff0 = data0.shape[0] - in_num
    print("\n原数据量：%d, 覆盖事件：%d, 数据损失：%d, 总事件类别：%d, 事件类别/国家 大于 %d 的国家有 %d 个. \n" % (
        data0.shape[0], in_num, diff0, num_all0, limit0, test_num))

    print("\n---All country number: %d ---\n" % len(all_cou_dic.keys()))
    num_sta0 = []
    num_1_5 = []
    num_6_10 = []
    num_11_15 = []
    num_over_16 = []

    for k0 in all_cou_dic.keys():
        num_v0 = len(all_cou_dic[k0])
        print("---%s: %d ---" % (k0, num_v0))
        num_sta0.append(num_v0)
        if (num_v0 > 0) and (num_v0 < 6):
            num_1_5.append(num_v0)
        elif (num_v0 > 5) and (num_v0 < 11):
            num_6_10.append(num_v0)
        elif (num_v0 > 10) and (num_v0 < 16):
            num_11_15.append(num_v0)
        else:
            num_over_16.append(num_v0)

    min0 = min(num_sta0)
    max0 = max(num_sta0)

    print("\n--- min: %d, max: %d ---\n" % (min0, max0))
    print("== between 1-5: count: %d == \n list: %s. \n" % (len(num_1_5), str(num_1_5)))
    print("== between 6-10: count: %d == \n list: %s. \n" % (len(num_6_10), str(num_6_10)))
    print("== between 11-15: count: %d == \n list: %s. \n" % (len(num_11_15), str(num_11_15)))
    print("== over 16: count: %d == \n list: %s. \n" % (len(num_over_16), str(num_over_16)))

    np.random.seed(1)
    train_dic0 = {}
    test_dic0 = {}
    for cou_k in all_cou_dic.keys():
        inc_k0 = len(all_cou_dic[cou_k])
        if (inc_k0 > 0) and (inc_k0 < 6):
            k_list0 = list(all_cou_dic[cou_k].keys())
            for n_or in k_list0:
                train_dic0[n_or] = all_cou_dic[cou_k][n_or]
        elif (inc_k0 > 5) and (inc_k0 < 20):
            k_list0 = list(all_cou_dic[cou_k].keys())
            c_k0 = np.random.choice(len(all_cou_dic[cou_k]), 1, replace=False)[0]
            choose_n0 = k_list0[c_k0]
            cou_na0 = choose_n0.split("_")[0]
            b0 = 1
            for n_or in all_cou_dic[cou_k].keys():
                if n_or != choose_n0:
                    n00 = cou_na0 + "_" + str(b0)
                    train_dic0[n00] = all_cou_dic[cou_k][n_or]
                    b0 += 1
            test_dic0[cou_na0 + "_" + str(1)] = all_cou_dic[cou_k][choose_n0]
        # elif (inc_k0 > 19) and (inc_k0 < 300):
        else:
            num_ch0 = int(inc_k0 / 10)
            k_list0 = list(all_cou_dic[cou_k].keys())
            c_k0 = list(np.random.choice(len(all_cou_dic[cou_k]), num_ch0,
                                         replace=False))
            choose_l0 = []
            for ind_k0 in c_k0:
                choose_l0.append(k_list0[ind_k0])
            choose_n0 = choose_l0[0]
            cou_na0 = choose_n0.split("_")[0]
            tra0 = 1
            tes0 = 1
            for n_or in all_cou_dic[cou_k].keys():
                if n_or not in choose_l0:
                    n00 = cou_na0 + "_" + str(tra0)
                    train_dic0[n00] = all_cou_dic[cou_k][n_or]
                    tra0 += 1
                else:
                    n00 = cou_na0 + "_" + str(tes0)
                    test_dic0[n00] = all_cou_dic[cou_k][n_or]
                    tes0 += 1

    columns_all0 = cart_n0[:-2] + [cart_n0[-1]] + [cart_n0[-2]] + ["m"]

    train_df0 = pd.DataFrame.from_dict(train_dic0, orient="index")
    train_df0.columns = columns_all0
    train_df0.drop(cart_n0[-1], axis=1, inplace=True)

    test_df0 = pd.DataFrame.from_dict(test_dic0, orient="index")
    test_df0.columns = columns_all0
    test_df0.drop(cart_n0[-1], axis=1, inplace=True)

    return train_df0, test_df0


# 选取特定年份信息
def data_year_filter(data0, col_name0, year_l0):
    """
    data0 = data_breach0
    col_name0 = "timeline.incident.year"
    year_l0 = year_list
    """
    index_l0 = []
    for i0 in data0.index:
        if not pd.isna(data0.loc[i0, col_name0]):
            if data0.loc[i0, col_name0] in year_l0:
                index_l0.append(i0)
    df0 = data0.loc[index_l0, ]
    diff0 = data0.shape[0] - df0.shape[0]
    print("原数据量：%d, 去除多余年份后, 新数据量：%d, 数据损失：%d. " % (data0.shape[0],
                                                    df0.shape[0], diff0))
    return df0


# 数据集加入年份信息
def data_breach_deal_year(year_l0, data0, g_ops0, title0):
    """
    year_l0 = year_list
    data0 = data_breach_or
    g_ops0 = global_ops
    title0 = "all_breach_cart_add_year.csv"
    """
    data_total_col0 = "attribute.confidentiality.data_total"
    data_breach0 = data_nan_filter(data0, data_total_col0)
    data_breach0 = data_year_filter(data_breach0, 'timeline.incident.year',
                                    year_l0)
    data_breach0 = drop_unknown(data_breach0, "victim.country.")

    country_time_dic0, country_test_set0 = sta_country_over_time(year_l0,
                                                                 data_breach0, 4)
    country_list0 = list(country_time_dic0.keys())

    employ_cat0 = search_employ(data_breach0, "victim.employee_count.")
    actor_cat0 = search_action(data_breach0, "actor")
    action_cat0 = search_action(data_breach0, "action")
    pattern_cat0 = search_action(data_breach0, "pattern")
    asset_cat0 = search_asset(data_breach0, "asset.variety.")
    data_cat0 = search_asset(data_breach0,
                             "attribute.confidentiality.data.variety.")

    part1_name0 = employ_cat0 + actor_cat0 + action_cat0
    part1_name0 = part1_name0 + pattern_cat0 + asset_cat0 + data_cat0
    part1_name0 = part1_name0 + country_list0
    data_part1_0 = data_breach0[part1_name0]
    data_part1_0, drop_index0 = tf_to_num(data_part1_0)
    data_breach0.drop(index=drop_index0, axis=0, inplace=True)

    year_dat0 = pd.get_dummies(data_breach0['timeline.incident.year'],
                               prefix='year',
                               prefix_sep='.', dummy_na=False)
    # unq_list0 = list(data_breach0['timeline.incident.year'].unique())    
    # print(str(list(year_dat0.columns)))
    part3_name0 = [data_total_col0, 'timeline.incident.year']
    data_part3_0 = data_breach0[part3_name0]
    data_part3_0 = pd.concat([data_part3_0, year_dat0], axis=1)
    data_part3_0.index = range(data_part3_0.shape[0])
    data_part1_0 = pd.concat([data_part1_0, data_part3_0], axis=1)

    # add to data0 
    sub_motive_name0 = search_motive_sub(data_breach0)
    sub_motive_dat0 = motive_sub_df(sub_motive_name0, data_breach0)
    sub_motive_cat0 = list(sub_motive_dat0.columns)
    sub_motive_dat0[sub_motive_cat0] = sub_motive_dat0[sub_motive_cat0].astype('int')

    industry_dat0 = pd.get_dummies(data_breach0['victim.industry.name'],
                                   prefix="victim.industry.name",
                                   prefix_sep='.', dummy_na=True)
    industry_cat0 = []
    for in0 in list(industry_dat0.columns):
        if (in0.split(".")[-1] != "nan") and (in0.split(".")[-1] != "Unknown") and (
                in0.split(".")[-1] != "483") and (in0.split(".")[-1] != "FALSE"):
            industry_cat0.append(in0)
    industry_dat0 = industry_dat0[industry_cat0]
    industry_dat0.index = range(industry_dat0.shape[0])

    # part2_name0 = sub_motive_cat0 + industry_cat0
    data_part2_0 = pd.concat([sub_motive_dat0, industry_dat0], axis=1)

    # all_data_name0 = part1_name0 + part2_name0
    all_data0 = pd.concat([data_part1_0, data_part2_0], axis=1)
    # industry_dat0[industry_cat0] = industry_dat0[industry_cat0].astype('bool')

    all_data0.to_csv(g_ops0 + title0, index=None)

    return all_data0


# 数据集加入年份信息，生成符合决策树信度模型的数据
def to_cart_data_year(data0, country0, cart_n0):
    """
    data0, country0 = data_breach, country_name
    cart_n0 = test_name_list
    """
    in_num = 0
    test_num = 0
    # min incident: 3
    limit0 = 3
    # cat num
    num_all0 = 0
    all_cou_dic = {}
    for cou0 in country0:
        c_n0 = cou0.split(".")[-1]
        df_cou0 = data0[data0[cou0] == 1]
        df_cou0 = df_cou0[cart_n0]
        index0 = df_cou0.index
        c_dic0 = {}
        str_chage0 = {}
        for i0 in index0:
            inc0 = list(df_cou0.loc[i0, :])
            cov_str0 = str(inc0[:-2] + [inc0[-1]])
            if cov_str0 not in str_chage0.keys():
                str_chage0[cov_str0] = inc0[:-2] + [inc0[-1]]
            if cov_str0 not in c_dic0.keys():
                c_dic0[cov_str0] = [inc0[-2]]
            else:
                c_dic0[cov_str0].append(inc0[-2])
        n_dic0 = {}
        label0 = 1
        cou_inc0 = 0
        for str0 in c_dic0.keys():
            l0 = c_dic0[str0]
            cov0 = str_chage0[str0]
            if len(l0) != 1:
                n_l0 = c_n0 + "_" + str(label0)
                label0 += 1
                cou_inc0 += len(l0)
                ave0 = round(float(sum(l0)) / len(l0), 2)
                cov0.append(ave0)
                cov0.append(len(l0))
                n_dic0[n_l0] = cov0
            else:
                if l0[0] > 0:
                    n_l0 = c_n0 + "_" + str(label0)
                    label0 += 1
                    cou_inc0 += len(l0)
                    cov0.append(l0[0])
                    cov0.append(len(l0))
                    n_dic0[n_l0] = cov0
                else:
                    continue

        if len(n_dic0.keys()) > limit0:
            num_all0 += len(n_dic0.keys())
            test_num += 1
            in_num += cou_inc0
            all_cou_dic[c_n0] = n_dic0

    diff0 = data0.shape[0] - in_num
    print("\n原数据量：%d, 覆盖事件：%d, 数据损失：%d, 总事件类别：%d, 事件类别/国家 大于 %d 的国家有 %d 个. \n" % (
        data0.shape[0], in_num, diff0, num_all0, limit0, test_num))

    print("\n---All country number: %d ---\n" % len(all_cou_dic.keys()))
    num_sta0 = []
    num_1_5 = []
    num_6_10 = []
    num_11_15 = []
    num_over_16 = []

    for k0 in all_cou_dic.keys():
        num_v0 = len(all_cou_dic[k0])
        print("---%s: %d ---" % (k0, num_v0))
        num_sta0.append(num_v0)
        if (num_v0 > 0) and (num_v0 < 6):
            num_1_5.append(num_v0)
        elif (num_v0 > 5) and (num_v0 < 11):
            num_6_10.append(num_v0)
        elif (num_v0 > 10) and (num_v0 < 16):
            num_11_15.append(num_v0)
        else:
            num_over_16.append(num_v0)

    min0 = min(num_sta0)
    max0 = max(num_sta0)

    print("\n--- min: %d, max: %d ---\n" % (min0, max0))
    print("== between 1-5: count: %d == \n list: %s. \n" % (len(num_1_5), str(num_1_5)))
    print("== between 6-10: count: %d == \n list: %s. \n" % (len(num_6_10), str(num_6_10)))
    print("== between 11-15: count: %d == \n list: %s. \n" % (len(num_11_15), str(num_11_15)))
    print("== over 16: count: %d == \n list: %s. \n" % (len(num_over_16), str(num_over_16)))

    np.random.seed(104)
    # best 105
    train_dic0 = {}
    test_dic0 = {}
    for cou_k in all_cou_dic.keys():
        inc_k0 = len(all_cou_dic[cou_k])
        num_ch0 = int(inc_k0 / 10) + 1
        k_list0 = list(all_cou_dic[cou_k].keys())
        c_k0 = list(np.random.choice(len(all_cou_dic[cou_k]), num_ch0,
                                     replace=False))
        choose_l0 = []
        for ind_k0 in c_k0:
            choose_l0.append(k_list0[ind_k0])
        choose_n0 = choose_l0[0]
        cou_na0 = choose_n0.split("_")[0]
        tra0 = 1
        tes0 = 1
        for n_or in all_cou_dic[cou_k].keys():
            if n_or not in choose_l0:
                n00 = cou_na0 + "_" + str(tra0)
                train_dic0[n00] = all_cou_dic[cou_k][n_or]
                tra0 += 1
            else:
                n00 = cou_na0 + "_" + str(tes0)
                test_dic0[n00] = all_cou_dic[cou_k][n_or]
                tes0 += 1

    columns_all0 = cart_n0[:-2] + [cart_n0[-1]] + [cart_n0[-2]] + ["m"]

    train_df0 = pd.DataFrame.from_dict(train_dic0, orient="index")
    train_df0.columns = columns_all0
    train_df0.drop(cart_n0[-1], axis=1, inplace=True)

    test_df0 = pd.DataFrame.from_dict(test_dic0, orient="index")
    test_df0.columns = columns_all0
    test_df0.drop(cart_n0[-1], axis=1, inplace=True)

    return train_df0, test_df0


if __name__ == '__main__':

    global_ops = "../data/"

    breach_ops = global_ops + "all_breach.csv"
    data_breach_or = pd.read_csv(breach_ops, low_memory=False)

    year_list = ["2019", "2018", "2017", "2016", "2015", "2014",
                 "2013", "2012", "2011", "2010"]

    breach_data = data_breach_deal(year_list, data_breach_or, global_ops,
                                   "all_breach_cart.csv")
    breach_data_new_year = data_breach_deal_year(year_list, data_breach_or,
                                                 global_ops,
                                                 "all_breach_cart_add_year.csv")

    breach_ops = global_ops + "all_breach_cart_add_year.csv"
    data_breach = pd.read_csv(breach_ops)

    year_list = ["2019", "2018", "2017", "2016", "2015", "2014",
                 "2013", "2012", "2011", "2010"]
    country_time_dic, country_test_set = sta_country_over_time(year_list,
                                                               data_breach, 4)

    country_name = list(country_time_dic.keys())
    cov_value_list, name_dic = name_cat(data_breach)
    # print(str(cov_value_list))

    high_cat_list = list(name_dic.keys())
    # print("=============== all cat: %s. ===============" % str(high_cat_list))           
    choose_list = [['victim.employee_count.', 'actor.'],
                   ['victim.employee_count.', 'pattern.'],
                   ['victim.employee_count.', 'actor.motive.'],
                   ['actor.', 'action.'],
                   ['actor.', 'pattern.'],
                   ['actor.', 'asset.variety.'],
                   ['actor.', 'actor.motive.'],
                   ['actor.', 'victim.industry.name.'],
                   ['action.', 'pattern.'],
                   ['action.', 'asset.variety.'],
                   ['action.', 'actor.motive.'],
                   ['pattern.', 'asset.variety.'],
                   ['pattern.', 'actor.motive.'],
                   ['asset.variety.', 'actor.motive.']]

    data_ops = "../data/"
    for ch0 in choose_list:
        print("=========== %s begin ===========" % str(ch0))
        # high_cat_sub_list = ch0 + ["year."]
        high_cat_sub_list = ch0
        test_name_list = search_high_cat(name_dic, high_cat_sub_list)
        test_name_list = test_name_list + ['timeline.incident.year']
        cart_train_df, cart_test_df = to_cart_data_year(data_breach,
                                                        country_name,
                                                        test_name_list)
        for n0 in range(len(test_name_list)):
            tmp = test_name_list[n0].rstrip()
            if tmp in tran_dic.keys():
                test_name_list[n0] = tran_dic[tmp]

        cart_train_df.columns = test_name_list[:-1] + ["m"]
        index_tra_dic = {"国家": list(cart_train_df.index)}
        index_tra_df = pd.DataFrame.from_dict(index_tra_dic)
        cart_train_df.index = range(len(cart_train_df.index))
        cart_train_df = pd.concat([index_tra_df, cart_train_df], axis=1)

        cart_test_df.columns = test_name_list[:-1] + ["m"]
        index_tes_dic = {"国家": list(cart_test_df.index)}
        index_tes_df = pd.DataFrame.from_dict(index_tes_dic)
        cart_test_df.index = range(len(cart_test_df.index))
        cart_test_df = pd.concat([index_tes_df, cart_test_df], axis=1)

        cat1_0 = ch0[0][:-1]
        cat2_0 = ch0[1][:-1]
        if cat1_0 in tran_dic.keys():
            cat1_0 = tran_dic[cat1_0]
        if cat2_0 in tran_dic.keys():
            cat2_0 = tran_dic[cat2_0]

        ops_train_file = data_ops + "data_train2_" + cat1_0
        ops_train_file = ops_train_file + "_" + cat2_0 + ".csv"
        cart_train_df.to_csv(ops_train_file, index=None,
                             encoding='utf_8')

        ops_test_file = data_ops + "data_test2_" + cat1_0
        ops_test_file = ops_test_file + "_" + cat2_0 + ".csv"
        cart_test_df.to_csv(ops_test_file, index=None,
                            encoding='utf_8')

        ops_train_file = data_ops + "data_train_" + cat1_0
        ops_train_file = ops_train_file + "_" + cat2_0 + ".csv"
        cart_train_df.to_csv(ops_train_file, index=None,
                             encoding='utf_8_sig')

        ops_test_file = data_ops + "data_test_" + cat1_0
        ops_test_file = ops_test_file + "_" + cat2_0 + ".csv"
        cart_test_df.to_csv(ops_test_file, index=None,
                            encoding='utf_8_sig')

        print("=========== %s end ===========\n" % str(ch0))
