# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 09:37:48 2020

@author: Zhaoke

文件说明：数据预处理 绘制描述性分析的图表

数据源：https://github.com/vz-risk/vcdb
"""

import os
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.render import make_snapshot
from snapshot_selenium import snapshot as driver
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Line
from pyecharts.charts import HeatMap


# 读入数据泄露数据集
def idf_read_csv(file_path0):
    # file_path0 = data_ops
    if os.path.splitext(file_path0)[1] != '.csv':
        return  # or whatever
    seps = [',', ';', '\t']
    encodings = [None, 'utf-8', 'ISO-8859-1']
    for sep0 in seps:
        for encoding0 in encodings:
            try:
                return pd.read_csv(file_path0, encoding=encoding0, sep=sep0,
                                   index_col="plus.created",
                                   low_memory=False)
            except (UnicodeDecodeError, Exception):
                pass
    raise ValueError("{!r} is has no encoding in {} or seperator in {}"
                     .format(file_path0, encodings, seps))


# 去除缺失数据
def drop_miss_data(or_csv0, new_ops0):
    data_drop_miss0 = or_csv0.dropna(axis=1, how="all")
    data_col0 = list(data_drop_miss0.columns)

    # the number of miss data is bigger than 50% of all data.
    del_col_para0 = int(data_drop_miss0.shape[0] / 2)

    for miss0 in data_col0:
        not_null_num = sum(pd.notnull(data_drop_miss0[miss0]))
        if not_null_num > del_col_para0:
            continue
        else:
            del data_drop_miss0[miss0]
            print("delete the column: %s. " % miss0)

    # new_ops0 = "D:/vcdb_new_2019_drop_miss.csv"
    data_drop_miss0.to_csv(new_ops0, index=None)

    return data_drop_miss0


# 数据泄露事件数量条形图
def bar_reversal_num(title0, name_list0, value_list0, label0, ops_reversal0):
    # print(title0)
    bar = Bar(init_opts=opts.InitOpts(width="640px", height="320px"))
    bar.add_xaxis(name_list0)
    bar.add_yaxis(label0, value_list0, category_gap="50%")
    bar.set_global_opts(title_opts=opts.TitleOpts(title="",
                                                  # subtitle = "副标题",
                                                  pos_bottom="0%",
                                                  pos_left="center"),
                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=14)),
                        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(font_size=14)),
                        legend_opts=opts.LegendOpts(is_show=False))
    bar.reversal_axis()
    bar.set_series_opts(label_opts=opts.LabelOpts(position="right", font_size=14),
                        itemstyle_opts=opts.ItemStyleOpts(color="#9A32CD"))

    if ops_reversal0.split(".")[-1] == "html":
        bar.render(ops_reversal0)
    else:
        make_snapshot(driver, bar.render(), ops_reversal0)

    return None


# 数据泄露事件数量占比条形图
def bar_reversal_pct(title0, name_list0, value_list0, label0, ops_reversal0):
    """
    title0, name_list0, value_list0 = action_subvar_all_bre, action_subvar_name, action_subvar_value,
    label0, ops_reversal0 = "事件占比", action_subvar_all_bre_ops
    title0, name_list0, value_list0, label0, ops_reversal0 = action_title0, action_name0, action_value0, action_label0, action_ops0
    """

    if "(" in title0:
        number0 = title0.split("(")[-1]
        label0 = label0 + " (" + number0

    name_len0 = []
    for n0 in name_list0:
        name_len0.append(len(n0))

    font_size0 = 20

    if (max(name_len0) < 7) and ("全部数据泄露事件威胁行为之" not in title0):
        bar = Bar(init_opts=opts.InitOpts(width="800px", height="400px"))
        bar.add_xaxis(name_list0)
        bar.add_yaxis(label0, value_list0, category_gap="50%")
        bar.set_global_opts(title_opts=opts.TitleOpts(title="",
                                                      pos_bottom="0%",
                                                      pos_left="center"),
                            xaxis_opts=opts.AxisOpts(
                                axislabel_opts=opts.LabelOpts(formatter="{value}%", font_size=font_size0)),
                            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-30, font_size=font_size0)),
                            legend_opts=opts.LegendOpts(is_show=True,
                                                        textstyle_opts=opts.TextStyleOpts(font_size=font_size0 + 1)))

        bar.reversal_axis()
        bar.set_series_opts(label_opts=opts.LabelOpts(position="right", font_size=font_size0,
                                                      formatter=JsCode(
                                                          "function(x){return Number(x.data.percent * 100).toFixed() "
                                                          "+ '%';}")),
                            itemstyle_opts=opts.ItemStyleOpts(color="#9A32CD"))
    else:
        font_size0 = 14
        if "全部数据泄露事件威胁行为之" in title0:
            cat_gap0 = "70%"
        else:
            cat_gap0 = "60%"
        name_list0.reverse()
        value_list0.reverse()
        bias0 = -18
        if len(name_list0) < 6:
            width0 = str(80 * (len(name_list0) + 2)) + "px"
        else:
            width0 = str(min(900, 80 * (len(name_list0)))) + "px"
        height0 = str(max(280, 40 * len(name_list0))) + "px"

        bar = Bar(init_opts=opts.InitOpts(width=width0, height=height0))
        bar.add_xaxis(name_list0)
        bar.add_yaxis(label0, value_list0, category_gap=cat_gap0)
        bar.set_global_opts(title_opts=opts.TitleOpts(title="",
                                                      pos_bottom="0%",
                                                      pos_left="center"),
                            legend_opts=opts.LegendOpts(is_show=True,
                                                        textstyle_opts=opts.TextStyleOpts(font_size=font_size0 + 1)),
                            xaxis_opts=opts.AxisOpts(
                                axislabel_opts=opts.LabelOpts(rotate=bias0, font_size=font_size0 + 1)),
                            yaxis_opts=opts.AxisOpts(
                                axislabel_opts=opts.LabelOpts(formatter="{value}%", font_size=font_size0 + 2)),
                            )

        bar.set_series_opts(label_opts=opts.LabelOpts(
            formatter=JsCode("function(x){return Number(x.data.percent * 100).toFixed() + '%';}"),
            font_size=font_size0 + 2),
            itemstyle_opts=opts.ItemStyleOpts(color="#9A32CD"))

    if ops_reversal0.split(".")[-1] == "html":
        bar.render(ops_reversal0)
    else:
        make_snapshot(driver, bar.render(), ops_reversal0)

    return None


# 威胁行为数据的事件数量的相关处理
def order_action_num(or_dat0):
    # or_dat0 = data_incident
    ac_dic_china = {"Error": "错误行为", "Hacking": "黑客袭击", "Misuse": "不当使用", "Physical": "物理操作",
                    "Malware": "恶意软件", "Social": "社交策略", "Unknown": "未知因素", "Environmental": "异常环境"}

    col_name0 = list(or_dat0.columns)
    ac_name_l0 = []
    ac_value_l0 = []
    ac_dic0 = {}

    for item0 in col_name0:
        if "action." in item0:
            if item0.count(".") == 1:
                if item0.split(".")[0] == "action":
                    tmp_value0 = or_dat0[(or_dat0[item0] == True) | (or_dat0[item0] == "TRUE")].shape[0]
                    ac_dic0[item0] = tmp_value0

    ac_dic_new0 = sorted(ac_dic0.items(), key=lambda d: d[1], reverse=False)

    for it0 in range(len(ac_dic_new0)):
        dic_key0 = ac_dic_new0[it0][0].split(".")[-1]
        if ac_dic_new0[it0][1] > 0:
            if dic_key0 in ac_dic_china.keys():
                ac_name_l0.append(ac_dic_china[dic_key0])
            else:
                ac_name_l0.append(dic_key0)
            ac_value_l0.append(ac_dic_new0[it0][1])

    return ac_name_l0, ac_value_l0, or_dat0.shape[0]


# 威胁行为数据的事件占比的相关处理
def order_action_pct(or_dat0):
    # or_dat0 = data_breach
    # or_dat0 = data0
    ac_dic_china = {"Error": "错误行为", "Hacking": "黑客袭击", "Misuse": "不当使用", "Physical": "物理操作",
                    "Malware": "恶意软件", "Social": "社交策略", "Unknown": "未知因素", "Environmental": "异常环境"}

    or_dat0 = or_dat0[(or_dat0['action.Unknown'] == False) | (or_dat0['action.Unknown'] == "FALSE")]
    or_dat0 = or_dat0[(or_dat0['action.Unknown'] != True) & (or_dat0['action.Unknown'] != "TRUE")]

    col_name0 = list(or_dat0.columns)
    ac_name_l0 = []
    ac_value_l0 = []
    ac_dic0 = {}

    for item0 in col_name0:
        if "action." in item0:
            if item0.count(".") == 1:
                if item0.split(".")[0] == "action":
                    if item0.split(".")[-1] != "Unknown":
                        tmp_value0 = or_dat0[(or_dat0[item0] == True) | (or_dat0[item0] == "TRUE")].shape[0]
                        ac_dic0[item0] = tmp_value0

    ac_dic_new0 = sorted(ac_dic0.items(), key=lambda d: d[1], reverse=False)

    for it0 in range(len(ac_dic_new0)):
        dic_key0 = ac_dic_new0[it0][0].split(".")[-1]
        if dic_key0 in ac_dic_china.keys():
            ac_name_l0.append(ac_dic_china[dic_key0])
        else:
            ac_name_l0.append(dic_key0)
        ac_value_l0.append(ac_dic_new0[it0][1])

    sum_num0 = or_dat0.shape[0]
    ac_value_l_n = []
    ac_name_l_n = []
    for it1 in range(len(ac_value_l0)):
        dic_v0 = {}
        value0 = float(ac_value_l0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 / sum_num0 * 100, 2)
        dic_v0["percent"] = value0 / sum_num0
        if value0 / sum_num0 > 0.01:
            ac_value_l_n.append(dic_v0)
            ac_name_l_n.append(ac_name_l0[it1])

    return ac_name_l_n, ac_value_l_n, sum_num0


# 受害者行业数据的事件数量的相关处理
def order_victim_industry_num(or_dat0):
    # or_dat0 = data_incident
    # or_dat0 = data0
    vi_dic_china = {"Healthcare": "医疗行业", "Public": "公共部门", "Finance": "金融行业", "Information": "信息行业",
                    "Educational": "教育行业", "Retail": "零售业", "Professional": "专业服务", "Other Services": "其他服务",
                    "Unknown": "未知", "Manufacturing": "制造业", "Administrative": "行政管理", "Accomodation": "住宿行业",
                    "Transportation": "交通行业", "Trade": "商业", "Entertainment": "娱乐行业", "Real Estate": "房地产",
                    "Utilities": "公共事业", "Construction": "建筑行业", "Mining": "矿业", "Management": "管理行业",
                    "Agriculture ": "农业"}

    ac_name_l0 = []
    ac_value_l0 = []

    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != 'Unknown']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != 'FALSE']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != '923']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != '483']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != '622']

    sum_num0 = or_dat0.shape[0]

    unq_df0 = pd.DataFrame(or_dat0['victim.industry.name'].value_counts())
    dat_name0 = list(unq_df0.index)
    dat_value0 = list(unq_df0['victim.industry.name'])

    for item0 in range(len(dat_name0)):
        tmp_name0 = dat_name0[item0].rstrip()
        if tmp_name0 in vi_dic_china.keys():
            if dat_value0[item0] > 0:
                ac_name_l0.append(vi_dic_china[tmp_name0])
                ac_value_l0.append(dat_value0[item0])

    if len(ac_name_l0) > 6:
        ac_name_l0 = ac_name_l0[0:6]
        ac_value_l0 = ac_value_l0[0:6]

    ac_name_l0.reverse()
    ac_value_l0.reverse()

    return ac_name_l0, ac_value_l0, sum_num0


# 受害者行业数据的事件占比的相关处理
def order_victim_industry_pct(or_dat0):
    # or_dat0 = data_breach
    # or_dat0 = data0
    vi_dic_china = {"Healthcare": "医疗行业", "Public": "公共部门", "Finance": "金融行业", "Information": "信息行业",
                    "Educational": "教育行业", "Retail": "零售业", "Professional": "专业服务", "Other Services": "其他服务",
                    "Unknown": "未知", "Manufacturing": "制造业", "Administrative": "行政管理", "Accomodation": "住宿行业",
                    "Transportation": "交通行业", "Trade": "商业", "Entertainment": "娱乐行业", "Real Estate": "房地产",
                    "Utilities": "公共事业", "Construction": "建筑行业", "Mining": "矿业", "Management": "管理行业",
                    "Agriculture ": "农业"}

    ac_name_l0 = []
    ac_value_l0 = []
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != 'Unknown']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != 'FALSE']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != '923']
    or_dat0 = or_dat0[or_dat0['victim.industry.name'] != '483']

    # 统计每个唯一值出现了多少次  
    unq_df0 = pd.DataFrame(or_dat0['victim.industry.name'].value_counts())
    dat_name0 = list(unq_df0.index)
    dat_value0 = list(unq_df0['victim.industry.name'])

    for item0 in range(len(dat_name0)):
        tmp_name0 = dat_name0[item0].rstrip()
        if tmp_name0 in vi_dic_china.keys():
            ac_name_l0.append(vi_dic_china[tmp_name0])
            ac_value_l0.append(dat_value0[item0])

    if len(ac_name_l0) > 6:
        ac_name_l0 = ac_name_l0[0:6]
        ac_value_l0 = ac_value_l0[0:6]

    ac_name_l0.reverse()
    ac_value_l0.reverse()

    sum_num0 = or_dat0.shape[0]
    ac_value_l_n = []
    ac_name_l_n = []

    for it1 in range(len(ac_value_l0)):
        dic_v0 = {}
        value0 = float(ac_value_l0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 / sum_num0 * 100, 2)
        dic_v0["percent"] = value0 / sum_num0
        if value0 / sum_num0 > 0.01:
            ac_value_l_n.append(dic_v0)
            ac_name_l_n.append(ac_name_l0[it1])

    return ac_name_l_n, ac_value_l_n, sum_num0


# 威胁者数据的事件数量的相关处理
def order_actor_num(or_dat0):
    # or_dat0 = data_incident
    # or_dat0 = data0
    act_dic_china = {"External": "外部人员", "Internal": "内部人员", "Partner": "合作伙伴", "Multiple": "多方势力"}

    ac_name_l0 = []
    ac_value_l0 = []
    sum_num0 = or_dat0.shape[0]

    unq_df0 = pd.DataFrame(or_dat0['Actor'].value_counts())
    dat_name0 = list(unq_df0.index)
    dat_value0 = list(unq_df0['Actor'])

    for item0 in range(len(dat_name0)):
        tmp_name0 = dat_name0[item0].rstrip()
        if tmp_name0 in act_dic_china.keys():
            if dat_value0[item0] > 0:
                ac_name_l0.append(act_dic_china[tmp_name0])
                ac_value_l0.append(dat_value0[item0])

    if len(ac_name_l0) > 6:
        ac_name_l0 = ac_name_l0[0:6]
        ac_value_l0 = ac_value_l0[0:6]

    ac_name_l0.reverse()
    ac_value_l0.reverse()

    return ac_name_l0, ac_value_l0, sum_num0


# 威胁者 威胁模式 数据的事件数量的相关处理
def order_actor_pattern_pct(or_dat0, name_0):
    """
    or_dat0 = data_breach
    name_0 = 'Actor'

    or_dat0 = data0
    name_0 = 'pattern'
    """
    act_dic_china = {"External": "外部人员", "Internal": "内部人员", "Partner": "合作伙伴", "Multiple": "多方势力",
                     "Point of Sale": "销售点", "Crimeware": "犯罪软件", "Payment Card Skimmers": "支付卡读取器",
                     "Cyber-Espionage": "网络间谍", "Lost and Stolen Assets": "遗失及被盗资产",
                     "Web Applications": "网络应用程序", "Everything Else": "其他", "Privilege Misuse": "特权滥用",
                     "Miscellaneous Errors": "各种错误", "Denial of Service": "系统服务中断"}

    # name_0 = 'pattern'
    # 破坏网络和系统可用性的攻击

    ac_name_l0 = []
    ac_value_l0 = []
    or_dat0 = or_dat0[or_dat0[name_0] != "FALSE"]
    or_dat0 = or_dat0[or_dat0[name_0] != "622"]
    or_dat0 = or_dat0[or_dat0[name_0] != "813"]

    unq_df0 = pd.DataFrame(or_dat0[name_0].value_counts())
    dat_name0 = list(unq_df0.index)
    dat_value0 = list(unq_df0[name_0])

    for item0 in range(len(dat_name0)):
        tmp_name0 = dat_name0[item0].rstrip()
        if tmp_name0 in act_dic_china.keys():
            ac_name_l0.append(act_dic_china[tmp_name0])
            ac_value_l0.append(dat_value0[item0])
        else:
            ac_name_l0.append(tmp_name0)
            ac_value_l0.append(dat_value0[item0])

    if name_0 == 'Actor':
        if len(ac_name_l0) > 6:
            ac_name_l0 = ac_name_l0[0:6]
            ac_value_l0 = ac_value_l0[0:6]

    ac_name_l0.reverse()
    ac_value_l0.reverse()

    sum_num0 = or_dat0.shape[0]
    ac_value_l_n = []
    ac_name_l_n = []

    for it1 in range(len(ac_value_l0)):
        dic_v0 = {}
        value0 = float(ac_value_l0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 / sum_num0 * 100, 2)
        dic_v0["percent"] = value0 / sum_num0
        if value0 / sum_num0 > 0.01:
            ac_value_l_n.append(dic_v0)
            ac_name_l_n.append(ac_name_l0[it1])

    return ac_name_l_n, ac_value_l_n, sum_num0


# 绘制威胁行为条形图
def ac_reversal(data0, action_title0, action_label0, global_ops0, file_type0):
    # data0, action_title0, action_label0, global_ops0, file_type0 = data_incident_2019, action_2019_inc_title,
    # label_item, global_ops, file_type data0, action_title0, action_label0, global_ops0, file_type0 = data_incident,
    #  action_all_incident_title, label_item, global_ops, file_type

    action_name0 = []
    action_value0 = []

    if action_label0 == "事件数量":
        action_name0, action_value0, num0 = order_action_num(data0)
        action_title0 = action_title0 + "数量 (样本总量：" + str(num0) + "件)"
    elif action_label0 == "事件占比":
        action_name0, action_value0, num0 = order_action_pct(data0)
        action_title0 = action_title0 + "占比 (样本总量：" + str(num0) + "件)"
    # action_title = "图片1：全部安全事件各类事故"
    # action_label = "事件数量"

    action_ops0 = global_ops0 + action_title0 + file_type0
    if action_label0 == "事件数量":
        bar_reversal_num(action_title0, action_name0, action_value0,
                         action_label0, action_ops0)
    elif action_label0 == "事件占比":
        bar_reversal_pct(action_title0, action_name0, action_value0,
                         action_label0, action_ops0)

    return None


# 绘制受威胁行业条形图
def vic_reversal(data0, action_title0, action_label0, global_ops0, file_type0):
    # data0, action_title0, action_label0, global_ops0, file_type0 = data_incident_2019, action_2019_inc_title,
    # label_item, global_ops, file_type data0, action_title0, action_label0, global_ops0, file_type0 = data_incident,
    #  victim_all_incident_title, label_item, global_ops, file_type

    action_name0 = []
    action_value0 = []

    if action_label0 == "事件数量":
        action_name0, action_value0, num0 = order_victim_industry_num(data0)
        action_title0 = action_title0 + "数量 (样本总量：" + str(num0) + "件)"
    elif action_label0 == "事件占比":
        action_name0, action_value0, num0 = order_victim_industry_pct(data0)
        action_title0 = action_title0 + "占比 (样本总量：" + str(num0) + "件)"

    action_ops0 = global_ops0 + action_title0 + file_type0
    if action_label0 == "事件数量":
        bar_reversal_num(action_title0, action_name0, action_value0,
                         action_label0, action_ops0)
    elif action_label0 == "事件占比":
        bar_reversal_pct(action_title0, action_name0, action_value0,
                         action_label0, action_ops0)

    return None


# 绘制威胁者条形图
def act_reversal(data0, action_title0, action_label0, name0,
                 global_ops0, file_type0):
    """
    data0, action_title0, action_label0 = data_incident_2019, action_2019_inc_title, label_item
    global_ops0, file_type0 = global_ops, file_type
    data0, action_title0, action_label0 = data_incident, victim_all_incident_title, label_item
    global_ops0, file_type0 = global_ops, file_type
    name0 = "Actor"
                 
    data0, action_title0 = data_breach_cn, actor_cn_bre_title
    action_label0, name0, global_ops0, file_type0 = label_item, "Actor", global_ops, file_type
    """
    action_name0 = []
    action_value0 = []

    if action_label0 == "事件数量":
        action_name0, action_value0, num0 = order_actor_num(data0)
        action_title0 = action_title0 + "数量 (样本总量：" + str(num0) + "件)"
    elif action_label0 == "事件占比":
        action_name0, action_value0, num0 = order_actor_pattern_pct(data0, name0)
        action_title0 = action_title0 + "占比 (样本总量：" + str(num0) + "件)"

    action_ops0 = global_ops0 + action_title0 + file_type0
    if action_label0 == "事件数量":
        bar_reversal_num(action_title0, action_name0, action_value0,
                         action_label0, action_ops0)
    elif action_label0 == "事件占比":
        bar_reversal_pct(action_title0, action_name0, action_value0,
                         action_label0, action_ops0)

    return None


# 绘制折线图
def smooth_line(search_name0, dat0, title_0, g_ops, type_0):
    """
    search_name0, dat0, title_0, g_ops, type_0 = actor_name, data_breach, actor_all_bre_time, global_ops, file_type
    """
    value_0, label_0 = line_data(search_name0, dat0)
    ops_0 = g_ops + title_0 + type_0
    time_series(title_0, value_0, label_0, ops_0)

    return None


# 获取动机子类
def motive_sub(data0):
    # data0 = data_breach

    motive_sub0 = ['Convenience', 'Espionage', 'Fear', 'Financial',
                   'Fun', 'Grudge', 'Ideology', 'Other', 'Secondary']

    search0 = ["actor.internal.motive.", "actor.external.motive.",
               "actor.partner.motive."]

    all_col0 = list(data0.columns)
    for cc in all_col0:
        if "motive" in cc:
            if cc.split(".")[-1] == "Unknown":
                data0 = data0[(data0[cc] == False) | (data0[cc] == "FALSE")]
                # data0[data0['actor.partner.motive.Unknown'] == True]

    dic_sub0 = {}
    for dic0 in motive_sub0:
        dic_sub0[dic0] = []

    dic_sub0['timeline.incident.year'] = []

    for index0 in list(data0.index):
        for m0 in motive_sub0:
            tmp_tf0 = False
            for name0 in search0:
                if (data0.loc[index0, name0 + m0] == True) or (data0.loc[index0, name0 + m0] == "TRUE"):
                    tmp_tf0 = True
                else:
                    continue
            dic_sub0[m0].append(tmp_tf0)
        temp_year0 = data0.loc[index0, 'timeline.incident.year']
        dic_sub0['timeline.incident.year'].append(temp_year0)

    motive_df0 = pd.DataFrame.from_dict(dic_sub0)

    return motive_df0


# 获取动机子数据集
def motive_sub_df(sub_list0, data0):
    # data0 = dat_bre0
    """
    sub_list0 = ['Convenience', 'Espionage', 'Fear', 'Financial',
                   'Fun', 'Grudge', 'Ideology', 'Other', 'Secondary']
    """
    search0 = ["actor.internal.motive.", "actor.external.motive.",
               "actor.partner.motive."]

    dic_sub0 = {}
    for dic0 in sub_list0:
        dic_sub0[dic0] = []

    for index0 in list(data0.index):
        for m0 in sub_list0:
            tmp_tf0 = False
            for name0 in search0:
                if (data0.loc[index0, name0 + m0] == True) or (data0.loc[index0, name0 + m0] == "TRUE"):
                    tmp_tf0 = True
                else:
                    continue
            dic_sub0[m0].append(tmp_tf0)

    motive_df0 = pd.DataFrame.from_dict(dic_sub0)

    return motive_df0


# 转化为折线图数据结构
def line_data(name_list0, data0):
    # name_list0, data0 = search_name0, dat0

    act_dic_china = {"External": "外部人员", "Internal": "内部人员", "Partner": "合作伙伴", "Multiple": "多方势力",
                     "Convenience": "方便的权宜之计", "Espionage": "间谍活动或竞争优势", "Fear": "恐惧或胁迫",
                     "Financial": "经济或个人利益", "Fun": "有趣、好奇或自豪", "Grudge": "怨恨或个人冒犯",
                     "Ideology": "意识形态或抗议", "Secondary": "协助发动另一场攻击",
                     "Organized crime": "有组织的犯罪集团", "Unaffiliated": "个人", "Cashier": "出纳员或服务员",
                     "Developer": "软件开发", "Doctor or nurse": "医生或护士", "End-user": "终端用户或正式员工",
                     "System admin": "系统或网络管理员", "State-affiliated": "国家支持或附属集团",
                     "Manager": "管理监管者", "Other": "其他", "Unknown": "未知"}

    if "Actor" in data0.columns:
        data0 = data0[data0["Actor"] != "FALSE"]
    # act_dic_china[""] = ""

    # data0 = data_breach
    # name_list0 = ["actor.External", "actor.Internal", "actor.Partner", "actor.Multiple"]
    dic_time0 = {}
    year_l0 = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017",
               "2018", "2019"]
    year_dic0 = {}

    for y0 in year_l0:
        data_tmp_0 = data0[(data0['timeline.incident.year'] == y0)]
        year_dic0[y0] = data_tmp_0.shape[0]

    for it0 in name_list0:
        data_tmp0 = data0[(data0[it0] == True) | (data0[it0] == "TRUE")]
        unq_df0 = pd.DataFrame(data_tmp0['timeline.incident.year'].value_counts())
        tmp_index0 = list(unq_df0.index)
        tmp_value0 = []
        for it1 in year_l0:
            if it1 in tmp_index0:
                tmp_pct0 = float(unq_df0.loc[it1, 'timeline.incident.year']) / year_dic0[it1] * 100
                tmp_value0.append(tmp_pct0)
            else:
                tmp_value0.append(0)
        if it0.split(".")[-1] in act_dic_china.keys():
            dic_n0 = act_dic_china[it0.split(".")[-1]]
        else:
            dic_n0 = it0.split(".")[-1]
        dic_time0[dic_n0] = tmp_value0

    return dic_time0, list(dic_time0.keys())


# 绘制折线图 图片设置
def time_series(title0, value_dic0, label0, ops0):

    # print(title0)
    """
    title0 = "dd"
    value_dic0 = dic_time0
    label0 = list(dic_time0.keys())
    ops0 = "./test.html"
    """
    year_l0 = ["2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017",
               "2018", "2019"]

    s_line0 = Line()

    s_line0.add_xaxis(year_l0)

    if len(label0) == 1:
        s_line0.add_yaxis(label0[0], value_dic0[label0[0]],
                          is_smooth=True,
                          is_symbol_show=False)
    elif len(label0) > 1:
        for it0 in label0:
            s_line0.add_yaxis(it0, value_dic0[it0],
                              is_smooth=True,
                              is_symbol_show=False)
    else:
        return None

    s_line0.set_global_opts(title_opts=opts.TitleOpts(title="",
                                                      pos_bottom="0%",
                                                      pos_left="center"),
                            legend_opts=opts.LegendOpts(is_show=True,
                                                        textstyle_opts=opts.TextStyleOpts(font_size=18)),
                            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}年", margin=15,
                                                                                   color="#ffffff63", font_size=18),
                                                     boundary_gap=False,
                                                     axisline_opts=opts.AxisLineOpts(is_show=True),
                                                     axistick_opts=opts.AxisTickOpts(is_show=True,
                                                                                     length=7,
                                                                                     linestyle_opts=opts.LineStyleOpts(
                                                                                         color="#ffffff1f")),
                                                     splitline_opts=opts.SplitLineOpts(
                                                         is_show=True,
                                                         linestyle_opts=opts.LineStyleOpts(color="#DEDEDE"))),
                            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}%", font_size=18)))

    if ops0.split(".")[-1] == "html":
        s_line0.render(ops0)
    else:
        make_snapshot(driver, s_line0.render(), ops0)

    return None


# 获取子类名称
def search_ac_var_sub(form_str0, data0):
    # data0 = data_breach
    # form_str0 = "actor."
    # form_str0, data0 = "action.", data_breach
    # sub_dic_action = search_ac_var_sub("action.", data_breach)
    sub_dic0 = {}
    colname0 = list(data0.columns)
    for it0 in colname0:
        if (form_str0 in it0) and (".variety." in it0):
            tmp_cat0 = it0.split(".")[1]
            tmp_sub0 = it0.split(".")[-1]
            if tmp_sub0 not in sub_dic0.keys():
                sub_dic0[tmp_sub0] = [tmp_cat0]
            else:
                sub_dic0[tmp_sub0].append(tmp_cat0)

    return sub_dic0


# 获取子类名称
def search_motive_sub(data0):
    # data0 = data_breach
    # form_str0 = "actor."
    # form_str0, data0 = "action.", data_breach
    # sub_dic_action = search_ac_var_sub("action.", data_breach)
    sub_dic0 = {}
    colname0 = list(data0.columns)
    for it0 in colname0:
        if ("actor." in it0) and (".motive." in it0):
            tmp_cat0 = it0.split(".")[1]
            tmp_sub0 = it0.split(".")[-1]
            if tmp_sub0 not in sub_dic0.keys():
                sub_dic0[tmp_sub0] = [tmp_cat0]
            else:
                sub_dic0[tmp_sub0].append(tmp_cat0)
    '''
    filter_name0 = []
    for k in list(sub_dic0.keys()):
        if k != 'NA' and k != 'Unknown':
            filter_name0.append(k)
    '''
    return list(sub_dic0.keys())


# 获取动机的数据集
def actor_var_data(form_str0, data0):
    # form_str0, data0 = "actor.", data_breach
    # sub_ac_dic0 = sub_dic0    
    sub_dic_0 = search_ac_var_sub(form_str0, data0)
    motive_sub0 = list(sub_dic_0.keys())

    for del0 in sub_dic_0["Unknown"]:
        all_name0 = "actor." + del0 + ".variety.Unknown"
        data0 = data0[(data0[all_name0] == False) | (data0[all_name0] == "FALSE")]

    dic_ac_sub0 = {}
    for dic0 in motive_sub0:
        dic_ac_sub0[dic0] = []

    dic_ac_sub0['timeline.incident.year'] = []

    for index0 in list(data0.index):
        for m0 in motive_sub0:
            tmp_tf0 = False
            for it0 in range(len(sub_dic_0[m0])):
                tmp_all_name0 = form_str0 + sub_dic_0[m0][it0] + ".variety." + m0
                if (data0.loc[index0, tmp_all_name0] == True) or (data0.loc[index0, tmp_all_name0] == "TRUE"):
                    tmp_tf0 = True
                else:
                    continue
            dic_ac_sub0[m0].append(tmp_tf0)
        temp_year0 = data0.loc[index0, 'timeline.incident.year']
        dic_ac_sub0['timeline.incident.year'].append(temp_year0)

    motive_df0 = pd.DataFrame.from_dict(dic_ac_sub0)
    motive_df0.drop('Unknown', axis=1, inplace=True)

    return motive_df0


# 获取威胁行为的数据集
def action_var_data(data0, form_str0):
    # sub_ac_dic0 = sub_dic0  
    # data0, form_str0 = data_breach, "action."
    sub_dic_0 = search_ac_var_sub(form_str0, data0)
    motive_sub0 = list(sub_dic_0.keys())

    for del0 in sub_dic_0["Unknown"]:
        all_name0 = "action." + del0 + ".variety.Unknown"
        data0 = data0[(data0[all_name0] == False) | (data0[all_name0] == "FALSE")]

    dic_ac_sub0 = {}
    for dic0 in motive_sub0:
        dic_ac_sub0[dic0] = []

    for index0 in list(data0.index):
        for m0 in motive_sub0:
            tmp_tf0 = False
            for it0 in range(len(sub_dic_0[m0])):
                tmp_all_name0 = form_str0 + sub_dic_0[m0][it0] + ".variety." + m0
                if (data0.loc[index0, tmp_all_name0] == True) or (data0.loc[index0, tmp_all_name0] == "TRUE"):
                    tmp_tf0 = True
                else:
                    continue
            dic_ac_sub0[m0].append(tmp_tf0)

    motive_df0 = pd.DataFrame.from_dict(dic_ac_sub0)
    all_num0 = motive_df0.shape[0]
    order_dic0 = {}

    for col_name0 in list(motive_df0.columns):
        t_num0 = float(motive_df0[(motive_df0[col_name0] == True)].shape[0])
        rate0 = t_num0 / all_num0
        order_dic0[col_name0] = rate0

    dic_new0 = sorted(order_dic0.items(), key=lambda d: d[1], reverse=True)
    top10_name0 = []
    top10_value0 = []

    for i0 in range(12):
        if dic_new0[i0][0] != 'Unknown' and len(top10_name0) < 10:
            top10_name0.append(dic_new0[i0][0])
            top10_value0.append(dic_new0[i0][1])

    top10_name0.reverse()
    top10_value0.reverse()

    sub_action_dic0 = {"Privilege abuse": "滥用系统访问权限", "Misdelivery": "发送错误", "Phishing": "网络钓鱼",
                       "Publishing error": "发布错误", "Theft": "盗窃", "Exploit vuln": "利用代码漏洞",
                       "Use of stolen creds": "使用被盗身份凭证", "Disposal error": "处理错误",
                       "Possession abuse": "滥用资产的物理访问", "Backdoor": "后门"}

    ac_name_l_n = []
    ac_value_l_n = []
    for it1 in range(len(top10_value0)):
        dic_v0 = {}
        value0 = float(top10_value0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 * 100, 2)
        dic_v0["percent"] = value0
        if value0 > 0.01:
            ac_value_l_n.append(dic_v0)
            if top10_name0[it1] in list(sub_action_dic0.keys()):
                ac_name_l_n.append(sub_action_dic0[top10_name0[it1]])
            else:
                ac_name_l_n.append(top10_value0)

    return ac_name_l_n, ac_value_l_n, all_num0


# 获取指定前缀的变量名
def search_single_form_col(data0, form_str0):
    # data0 = data_breach
    # form_str0 = "asset.variety."
    # form_str0 = "asset.assets.variety."
    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if form_str0 in it0:
            col_name_list0.append(it0)

    return col_name_list0


# 获取制定中间名称的变量名
def search_action_sub(data0, form_str0, mid_str0):
    """
    data0 = data_breach
    form_str0 = "action."
    mid_str0 = ".variety."
    """
    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if (form_str0 in it0) and (mid_str0 in it0):
            col_name_list0.append(it0)

    return col_name_list0


# 受威胁资产预处理
def diff_bar_pre_asset(dat0, f_str0):
    # dat0, f_str0 = data0, form_str0
    col_l0 = search_single_form_col(dat0, f_str0)

    year_l0 = ["2014", "2019"]
    year_dic0 = {}

    for y0 in year_l0:
        data_tmp_0 = dat0[(dat0['timeline.incident.year'] == y0)]
        year_dic0[y0] = data_tmp_0.shape[0]

    diff_dic0 = {}

    # col0 = col_l0[4]
    for col0 in col_l0:
        y_2014_tmp = dat0[((dat0[col0] == True) | (dat0[col0] == "TRUE")) & (
                dat0["timeline.incident.year"] == year_l0[0])].shape[0]
        y_2014_pct = float(y_2014_tmp) / year_dic0[year_l0[0]] * 100
        y_2019_tmp = dat0[((dat0[col0] == True) | (dat0[col0] == "TRUE")) & (
                dat0["timeline.incident.year"] == year_l0[1])].shape[0]
        y_2019_pct = float(y_2019_tmp) / year_dic0[year_l0[1]] * 100
        diff_tmp = round(y_2019_pct - y_2014_pct, 2)
        if abs(diff_tmp) > 1:
            diff_dic0[col0.split(".")[-1]] = diff_tmp

    or_diff_dic0 = sorted(diff_dic0.items(), key=lambda d: d[1], reverse=True)

    name_l0 = []
    value_l0 = []

    # 受威胁资产英汉翻译词典
    asset_dic0 = {"Server": "服务器", "Kiosk/Term": "自助服务终端", "Unknown": "未知", "User Dev": "用户设备",
                  "Media": "媒介", "Person": "人员", "Embedded": "嵌入式设备"}

    # ['Server', 'Kiosk/Term', 'Unknown', 'User Dev', 'Media']
    for it0 in range(len(or_diff_dic0)):
        name_l0.append(asset_dic0[or_diff_dic0[it0][0]])
        value_l0.append(or_diff_dic0[it0][1])

    return name_l0, value_l0


# 获取指定前缀的变量名
def search_action(data0, form_str0):
    # data0 = data_breach
    # form_str0 = "asset.variety."
    # form_str0 = "action."
    col_name_list0 = []
    colname0 = list(data0.columns)
    for it0 in colname0:
        if it0.count(".") == 1:
            if it0.split(".")[0] == form_str0:
                col_name_list0.append(it0)

    return col_name_list0


# 威胁行为预处理
def diff_bar_pre_action(dat0, f_str0):
    # dat0, f_str0 = data_breach, form_str0
    # dat0, f_str0 = data_breach, "action"

    dat0 = dat0[(dat0['action.Unknown'] == False) | (dat0['action.Unknown'] == "FALSE")]

    # dat0.drop('action.Unknown', axis=1, inplace=True)

    col_l0 = search_action(dat0, f_str0)

    year_l0 = ["2014", "2019"]
    year_dic0 = {}

    for y0 in year_l0:
        data_tmp_0 = dat0[(dat0['timeline.incident.year'] == y0)]
        year_dic0[y0] = data_tmp_0.shape[0]

    diff_dic0 = {}

    # col0 = col_l0[4]
    for col0 in col_l0:
        y_2014_tmp = dat0[((dat0[col0] == True) | (dat0[col0] == "TRUE")) & (
                dat0["timeline.incident.year"] == year_l0[0])].shape[0]
        y_2014_pct = float(y_2014_tmp) / year_dic0[year_l0[0]] * 100
        y_2019_tmp = dat0[((dat0[col0] == True) | (dat0[col0] == "TRUE")) & (
                dat0["timeline.incident.year"] == year_l0[1])].shape[0]
        y_2019_pct = float(y_2019_tmp) / year_dic0[year_l0[1]] * 100
        diff_tmp = round(y_2019_pct - y_2014_pct, 2)
        if abs(diff_tmp) > 1:
            diff_dic0[col0.split(".")[-1]] = diff_tmp

    or_diff_dic0 = sorted(diff_dic0.items(), key=lambda d: d[1], reverse=True)

    name_l0 = []
    value_l0 = []

    # 威胁行为词典
    ac_dic_china = {"Error": "错误行为", "Hacking": "黑客袭击", "Misuse": "不当使用", "Physical": "物理操作",
                    "Malware": "恶意软件", "Social": "社交策略", "Unknown": "未知因素", "Environmental": "异常环境"}

    # ['Server', 'Kiosk/Term', 'Unknown', 'User Dev', 'Media']
    for it0 in range(len(or_diff_dic0)):
        name_l0.append(ac_dic_china[or_diff_dic0[it0][0]])
        value_l0.append(or_diff_dic0[it0][1])

    return name_l0, value_l0


# 绘制增长下降条形图
def diff_bar(title0, name_l0, value_l0, label0, g_ops0, type0):
    # title0, name_l0, value_l0, label0 = asset_all_bre_diff, asset_name, asset_value, "增高/降低百分比"
    # g_ops0, type0 = global_ops, file_type
    y = []
    for idx, item in enumerate(name_l0):
        if value_l0[idx] > 0:
            y.append(
                opts.BarItem(
                    name=item,
                    value=value_l0[idx],
                    itemstyle_opts=opts.ItemStyleOpts(color="#749f83"),
                )
            )
        else:
            y.append(
                opts.BarItem(
                    name=item,
                    value=value_l0[idx],
                    itemstyle_opts=opts.ItemStyleOpts(color="#d48265"),
                )
            )

    font_size0 = 18
    c = Bar()
    c.add_xaxis(name_l0)
    c.add_yaxis(label0, y, category_gap="80%")
    c.set_global_opts(title_opts=opts.TitleOpts(title="",
                                                pos_bottom="0%",
                                                pos_left="center"),
                      yaxis_opts=opts.AxisOpts(
                          axislabel_opts=opts.LabelOpts(formatter="{value}%", font_size=font_size0)),
                      xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-20, font_size=font_size0)),
                      legend_opts=opts.LegendOpts(is_show=True,
                                                  textstyle_opts=opts.TextStyleOpts(font_size=font_size0)))
    c.set_series_opts(label_opts=opts.LabelOpts(font_size=font_size0))
    f_ops0 = g_ops0 + title0 + type0
    if type0 == ".html":
        c.render(f_ops0)
    else:
        make_snapshot(driver, c.render(), f_ops0)

    return None


# 处理威胁行为各子类的数据
def order_subaction_pct(or_dat0):
    # or_dat0 = data_breach
    # or_dat0 = sub_df_dic0["error"]
    ac_dic_china = {"Misconfiguration": "错误配置", "Loss": "丢失或错位", "Disposal error": "处理错误", "Publishing error": "发布错误",
                    "Misdelivery": "发送错误", "Brute force": "蛮力或密码猜测攻击", "Exploit vuln": "利用代码漏洞",
                    "Use of backdoor or C2": "使用后门或C2", "Use of stolen creds": "使用被盗身份凭证", "Unknown": "未知",
                    "Spyware/Keylogger": "捕获用户输入或操作", "Downloader": "下载或更新", "Capture stored data": "捕获系统磁盘数据",
                    "C2": "命令和控制通道", "Backdoor": "后门", "Unapproved hardware": "使用未批准硬件或设备",
                    "Data mishandling": "未批准方式处理数据", "Knowledge abuse": "滥用私人或委托的知识", "Possession abuse": "滥用资产的物理访问",
                    "Privilege abuse": "滥用系统访问权限", "Surveillance": "监视", "Skimmer": "安装读卡机侧录器",
                    "Disabled controls": "使物理屏障失效", "Tampering": "篡改", "Theft": "盗窃", "Forgery": "伪造",
                    "Pretexting": "利用虚构场景对话", "Bribery": "贿赂", "Phishing": "网络钓鱼", "Omission": "遗漏", "Other": "其他",
                    "Programming error": "编程错误", "Gaffe": "社交或言语失误", "Abuse of functionality": "功能滥用", "SQLi": "资料隐码攻击",
                    "Scan network": "扫描网络", "Export data": "导出数据", "Snooping": "窥探", "Assault": "威胁或身体暴力",
                    "Bypassed controls": "绕过物理障碍或控制", "Extortion": "敲诈勒索", "Influence": "影响策略",
                    "Email misuse": "电子邮件不当使用", "Inadequate processes": "进程不充分", "Carelessness": " 粗心",
                    "Backdoor or C2": "后门或C2", "Web application": "网络应用", "Remote injection": "远程注入",
                    "Download by malware": "本地恶意软件", "Email link": "电子邮件嵌入式链接", "Web drive-by": "自动执行或驱动感染",
                    "Direct install": "威胁代理直接安装", "Email attachment": "用户已发送附件", "Non-corporate": "非企业设施或网络",
                    "Remote access": "远程连接VPN", "Physical access": "物理访问或连接", "LAN access": "公司本地网络接入",
                    "Partner facility": "合作伙伴设施或区域", "Personal vehicle": "个人媒介", "Public facility": "公共设施或区域",
                    "Victim grounds": "受害者户外场地", "Victim public area": "受害公众或顾客区", "Victim work area": "受害者私人/工作区域",
                    "SMS": "短信", "Documents": "文件", "Phone": "电话", "In-person": "面对面", "Email": "电子邮件",
                    "Desktop sharing software": "桌面共享", "Victim secure area": "高安全区域", "Executive": "负法律责任的职员",
                    "Finance": "财会人员", "Human resources": "人力资源职员", "System admin": "系统或网络管理员",
                    "End-user or employee": "终端用户/普通员工", "Call center": "客服职员", "Cashier": "出纳员", "Customer": "顾客"}

    col_name0 = list(or_dat0.columns)
    ac_name_l0 = []
    ac_value_l0 = []

    ac_dic0 = {}
    for item0 in col_name0:
        tmp_value0 = or_dat0[(or_dat0[item0] == True) | (or_dat0[item0] == "TRUE")].shape[0]
        # ac_value_l0.append(tmp_value0)
        ac_dic0[item0] = tmp_value0

    ac_dic_new0 = sorted(ac_dic0.items(), key=lambda d: d[1], reverse=False)

    for it0 in range(len(ac_dic_new0)):
        dic_key0 = ac_dic_new0[it0][0].split(".")[-1]
        if dic_key0 in ac_dic_china.keys():
            ac_name_l0.append(ac_dic_china[dic_key0])
        else:
            ac_name_l0.append(dic_key0)
        ac_value_l0.append(ac_dic_new0[it0][1])

    sum_num0 = or_dat0.shape[0]
    ac_value_l_n = []
    ac_name_l_n = []

    for it1 in range(len(ac_value_l0)):
        dic_v0 = {}
        value0 = float(ac_value_l0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 / sum_num0 * 100, 2)
        dic_v0["percent"] = value0 / sum_num0
        if value0 / sum_num0 > 0.01:
            ac_value_l_n.append(dic_v0)
            ac_name_l_n.append(ac_name_l0[it1])

    return ac_name_l_n, ac_value_l_n, sum_num0


# 威胁行为各子类占比图
def action_sub_top(form_str0, data0, begin_num0, mid_str0,
                   global_ops0, file_type0):
    """
    form_str0, data0 = "action.", data_breach
    global_ops0, file_type0 = global_ops, file_type

    mid_str0 = ".variety."
    begin_num0 = 25

    mid_str0 = ".vector."
    begin_num0 = 26

    mid_str0 = ".target."
    begin_num0 = 37
    """
    data0 = data0[(data0['action.Unknown'] == False) | (data0['action.Unknown'] == "FALSE")]

    sub_dic_0 = search_ac_var_sub("action.", data0)
    for del0 in sub_dic_0["Unknown"]:
        all_name0 = "action." + del0 + mid_str0 + "Unknown"
        if all_name0 in data0.columns:
            data0 = data0[(data0[all_name0] == False) | (data0[all_name0] == "FALSE")]

    ac_dic_china = {"error": "错误行为", "hacking": "黑客袭击", "misuse": "不当使用", "physical": "物理操作",
                    "malware": "恶意软件", "social": "社交策略", "unknown": "未知因素", "environmental": "异常环境"}

    sub_dic0 = {}
    colname0 = list(data0.columns)
    for it0 in colname0:
        if (form_str0 in it0) and (mid_str0 in it0):
            mid0 = it0.split(".")[1]
            if mid0 not in list(sub_dic0.keys()):
                sub_dic0[mid0] = [it0]
            else:
                sub_dic0[mid0].append(it0)

    sub_df_dic0 = {}
    for it1 in list(sub_dic0.keys()):
        # str.capitalize()
        cat0 = form_str0 + str.capitalize(it1)
        tmp_df0 = data0[(data0[cat0] == True) | (data0[cat0] == "TRUE")]
        if tmp_df0.shape[0] != 0:
            sub_df_dic0[it1] = tmp_df0[sub_dic0[it1]]

    key_list0 = list(sub_df_dic0.keys())

    mid_cn0 = {".vector.": "途径", ".target.": "攻击目标", ".variety.": "行为"}

    for it2 in range(len(key_list0)):
        tmp_name0, tmp_value0, sum_0 = order_subaction_pct(sub_df_dic0[key_list0[it2]])
        if len(tmp_name0) > 7:
            tmp_name0 = tmp_name0[-7:]
            tmp_value0 = tmp_value0[-7:]
        # print(str(tmp_name0))
        action_title0 = "图片" + str(begin_num0 + it2 * 2) + "：全部数据泄露事件威胁行为之"
        action_title0 = action_title0 + ac_dic_china[key_list0[it2]]
        action_title0 = action_title0 + "各" + mid_cn0[mid_str0] + "子类占比 (样本总量："
        action_title0 = action_title0 + str(sum_0) + "件)"
        action_ops0 = global_ops0 + action_title0 + file_type0
        bar_reversal_pct(action_title0, tmp_name0, tmp_value0,
                         "事件占比", action_ops0)
    return None


# 计算受威胁资产子类占比
def order_subasset_pct(or_dat0):
    # or_dat0 = asset_sub_df0

    asset_dic0 = {"S": "服务器", "Other": "其他", "Unknown": "未知", "U": "用户设备", "M": "媒介", "P": "人员",
                  "N": "网络", "T": "公用终端机", "E": "嵌入式设备"}

    asset_sub_dic0 = {"Payment card": "支付卡", "Mobile phone": "手机", "ATM": "ATM", "Mail": "邮件",
                      "Desktop": "台式电脑", "Desktop or laptop": "台式/笔记本电脑", "Web application": "网络应用程序",
                      "Documents": "文件", "Database": "数据库", "Unknown": "未知"}

    col_name0 = list(or_dat0.columns)
    ac_name_l0 = []
    ac_value_l0 = []

    ac_dic0 = {}
    for item0 in col_name0:
        tmp_value0 = or_dat0[(or_dat0[item0] == True) | (or_dat0[item0] == "TRUE")].shape[0]
        # ac_value_l0.append(tmp_value0)
        ac_dic0[item0] = tmp_value0

    ac_dic_new0 = sorted(ac_dic0.items(), key=lambda d: d[1], reverse=False)

    for it0 in range(len(ac_dic_new0)):
        dic_key0 = ac_dic_new0[it0][0].split(".")[-1]
        if "-" in dic_key0:
            head_str0 = dic_key0.split("-")[0].rstrip()
            tail_str0 = dic_key0.split("-")[1].lstrip()
            if tail_str0 == "Unknown":
                continue
            if head_str0 in asset_dic0.keys():
                head_str0 = asset_dic0[head_str0]
            if tail_str0 in asset_sub_dic0.keys():
                tail_str0 = asset_sub_dic0[tail_str0]
            ac_name_l0.append(head_str0 + "-" + tail_str0)
            ac_value_l0.append(ac_dic_new0[it0][1])
        else:
            if dic_key0 == "Unknown":
                continue
            if dic_key0 in asset_dic0.keys():
                ac_name_l0.append(asset_dic0[dic_key0])
            else:
                ac_name_l0.append(dic_key0)
            ac_value_l0.append(ac_dic_new0[it0][1])

    sum_num0 = or_dat0.shape[0]
    ac_value_l_n = []
    ac_name_l_n = []

    for it1 in range(len(ac_value_l0)):
        dic_v0 = {}
        value0 = float(ac_value_l0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 / sum_num0 * 100, 2)
        dic_v0["percent"] = value0 / sum_num0
        if value0 / sum_num0 > 0.02:
            ac_value_l_n.append(dic_v0)
            ac_name_l_n.append(ac_name_l0[it1])

    return ac_name_l_n, ac_value_l_n, sum_num0


# 绘制受威胁资产子类占比图
def asset_sub_top(f_str0, dat0, begin_num0, global_ops0, file_type0):
    """
    f_str0 = "asset.assets.variety."
    dat0 = data_breach
    begin_num0 = 38
    """
    dat0 = dat0[(dat0["asset.assets.variety.Unknown"] == False) | (dat0["asset.assets.variety.Unknown"] == "FALSE")]

    asset_sub_list0 = search_single_form_col(dat0, f_str0)
    asset_sub_df0 = dat0[asset_sub_list0]
    asset_sub_name0, asset_sub_value0, num0 = order_subasset_pct(asset_sub_df0)

    asset_sub_title0 = "图片" + str(begin_num0)
    asset_sub_title0 = asset_sub_title0 + "：全部数据泄露事件各受威胁资产子类占比"
    asset_sub_title0 = asset_sub_title0 + " (样本总量：" + str(num0) + "件)"
    action_ops0 = global_ops0 + asset_sub_title0 + file_type0
    bar_reversal_pct(asset_sub_title0, asset_sub_name0, asset_sub_value0,
                     "事件占比", action_ops0)
    return None


# 计算泄露数据类型占比
def data_variety_pct(or_dat0, title_0, begin_num0, g_ops0, type0):
    """
    or_dat0 = data_breach
    g_ops0, type0 = global_ops, file_type
    title_0 = "全部数据泄露事件各泄露数据类型占比"
    label_0 = "事件占比"
    begin_num0 = 39
    """
    ac_dic_china = {"Other": "其他", "Classified": "机密情报", "System": "系统信息", "Bank": "银行账户",
                    "Secrets": "商业机密", "Internal": "敏感的内部数据", "Credentials": "认证凭证",
                    "Payment": "支付卡数据", "Unknown": "未知", "Medical": "医疗记录", "Personal": "个人或身份信息"}

    del0 = "attribute.confidentiality.data.variety.Unknown"
    or_dat0 = or_dat0[(or_dat0[del0] == False) | (or_dat0[del0] == "FALSE")]

    col_name0 = list(or_dat0.columns)
    ac_name_l0 = []
    ac_value_l0 = []

    ac_dic0 = {}
    for item0 in col_name0:
        if "attribute.confidentiality.data.variety." in item0:
            # ac_name_l0.append(item0)
            # item0 = ac_name_l0[0]                    
            tmp_value0 = or_dat0[(or_dat0[item0] == True) | (or_dat0[item0] == "TRUE")].shape[0]
            # ac_value_l0.append(tmp_value0)
            ac_dic0[item0] = tmp_value0

    ac_dic_new0 = sorted(ac_dic0.items(), key=lambda d: d[1], reverse=False)

    for it0 in range(len(ac_dic_new0)):
        dic_key0 = ac_dic_new0[it0][0].split(".")[-1]
        if dic_key0 in ac_dic_china.keys():
            ac_name_l0.append(ac_dic_china[dic_key0])
        else:
            ac_name_l0.append(dic_key0)
        ac_value_l0.append(ac_dic_new0[it0][1])

    sum_num0 = or_dat0.shape[0]
    ac_value_l_n = []
    ac_name_l_n = []
    for it1 in range(len(ac_value_l0)):
        dic_v0 = {}
        value0 = float(ac_value_l0[it1])
        # dic_v0["value"] = value0
        dic_v0["value"] = round(value0 / sum_num0 * 100, 2)
        dic_v0["percent"] = value0 / sum_num0
        if value0 / sum_num0 > 0.01:
            ac_value_l_n.append(dic_v0)
            ac_name_l_n.append(ac_name_l0[it1])

    # title_0 = "全部数据泄露事件各威胁行为子类占比"
    all_title0 = "图片" + str(begin_num0) + "：" + title_0
    all_title0 = all_title0 + " (样本总量：" + str(sum_num0) + "件)"
    ops_0 = g_ops0 + all_title0 + type0
    bar_reversal_pct(all_title0, ac_name_l_n, ac_value_l_n,
                     "事件占比", ops_0)
    return None


# 计算各威胁模式占比
def pattern_pct(or_dat0, title_0, begin_num0, label_0, name_0,
                g_ops0, type0):
    """
    or_dat0, title_0, begin_num0, label_0, name_0 = data_breach, "全部数据泄露事件各数据泄露模式占比", 28, "事件占比", "pattern"
    g_ops0, type0 = global_ops, file_type
    """
    ac_name_l_n, ac_value_l_n, num0 = order_actor_pattern_pct(or_dat0, name_0)
    all_title0 = "图片" + str(begin_num0) + "：" + title_0 + " (样本总量：" + str(num0) + "件)"
    ops_0 = g_ops0 + all_title0 + type0
    bar_reversal_pct(all_title0, ac_name_l_n, ac_value_l_n,
                     label_0, ops_0)
    return None


# 威胁行为子类和受威胁资产子类组合信息统计
def csv_as_table(data0, x_list0, y_list0, title_0, g_ops0, type0,
                 x_min0, y_min0, all_min0):
    """
    data0 = data_breach
    x_list0 = search_action_sub(data0, "action.", ".variety.")
    y_list0 = search_single_form_col(data0, "asset.assets.variety.")
    begin_num0 = 41
    label_0 = "事件占比"
    g_ops0, type0 = global_ops, ".csv"
    title_0 = "全部数据泄露事件威胁行为子类和受威胁资产子类组合Top10"
    x_min0, y_min0, all_min0 = 50, 50, 50

    data0, x_list0, y_list0 = data0, action_sub_list0, asset_sub_list0
    title_0, g_ops0, type0 = table_action_asset0, g_ops0, table_type0
    x_min0, y_min0, all_min0 = 0, 0, 0
    """

    table_ops0 = g_ops0 + title_0 + type0
    new_dat0 = data0[x_list0 + y_list0]

    x_new_list0 = []
    y_new_list0 = []

    for x_0 in x_list0:
        x_sta0 = new_dat0[((new_dat0[x_0] == True) | (new_dat0[x_0] == "TRUE"))].shape[0]
        if x_sta0 > x_min0:
            x_new_list0.append(x_0)
    for y_0 in y_list0:
        y_sta0 = new_dat0[((new_dat0[y_0] == True) | (new_dat0[y_0] == "TRUE"))].shape[0]
        if y_sta0 > y_min0:
            y_new_list0.append(y_0)

    ops_dic0 = {}
    for x0 in range(len(x_new_list0)):
        x_n = x_new_list0[x0]
        if x_n[-7:] == "Unknown":
            continue
        for y0 in range(len(y_new_list0)):
            key_tmp = str(x0) + "_" + str(y0)
            y_n = y_new_list0[y0]
            if y_n[-7:] == "Unknown":
                continue
            value_tmp = new_dat0[((new_dat0[x_n] == True) | (new_dat0[x_n] == "TRUE")) &
                                 ((new_dat0[y_n] == True) | (new_dat0[y_n] == "TRUE"))].shape[0]
            if value_tmp > all_min0:
                ops_dic0[key_tmp] = value_tmp

    order_ops_dic0 = sorted(ops_dic0.items(), key=lambda d: d[1], reverse=True)
    order_ops_dic0 = order_ops_dic0[0:10]

    table_dic0 = {"威胁行为子类": [], "受威胁资产子类": [], "事件数量": []}

    action_dic0 = {"error": "错误行为", "hacking": "黑客袭击", "misuse": "不当使用", "physical": "物理操作",
                   "malware": "恶意软件", "social": "社交策略", "unknown": "未知因素", "environmental": "异常环境"}

    action_sub_dic0 = {"Privilege abuse": "滥用系统访问权限", "Misdelivery": "发送错误", "Phishing": "网络钓鱼",
                       "Publishing error": "发布错误", "Theft": "盗窃", "Exploit vuln": "利用代码漏洞",
                       "Use of stolen creds": "使用被盗身份凭证", "Disposal error": "处理错误",
                       "Possession abuse": "滥用资产的物理访问", "Backdoor": "后门", "Unknown": "未知",
                       "C2": "命令和控制通道", "Capture stored data": "捕获系统磁盘数据",
                       "Loss": "丢失或错位", "Tampering": "篡改", "Skimmer": "安装读卡机侧录器",
                       "Disabled controls": "使物理屏障失效", "Surveillance": "监视", "SQLi": "资料隐码攻击",
                       "Misconfiguration": "错误配置", "Unapproved hardware": "使用未批准硬件或设备",
                       "Ram scraper": "内存中捕获数据", "Capture app data": "从应用程序或系统进程捕获数据",
                       "Use of backdoor or C2": "使用后门或C2", "Scan network": "扫描网络",
                       "Spyware/Keylogger": "捕获用户输入或操作"}

    asset_dic0 = {"S": "服务器", "Other": "其他", "Unknown": "未知", "U": "用户设备", "M": "媒介", "P": "人员",
                  "N": "网络", "T": "公用终端机", "E": "嵌入式设备"}

    asset_sub_dic0 = {"Payment card": "支付卡", "Mobile phone": "手机", "ATM": "ATM", "Mail": "邮件",
                      "Desktop": "台式电脑", "Desktop or laptop": "台式电脑/笔记本电脑",
                      "Web application": "网络应用程序", "Documents": "文件",
                      "Database": "数据库", "Unknown": "未知", "Gas terminal": "加油站", "End": "终端用户",
                      "POS terminal": "POS机终端", "POS controller": "POS机控制器", "File": "文件"}

    # asset_sub_dic0[""] = ""

    need_translate_ac0 = []
    need_translate_as0 = []

    for item0 in order_ops_dic0:
        num1 = int(item0[0].split("_")[0])
        num2 = int(item0[0].split("_")[1])

        col1_b = x_new_list0[num1].split(".")[1]
        col1_e = x_new_list0[num1].split(".")[-1]
        if col1_b in action_dic0.keys():
            col1_b = action_dic0[col1_b]
        if col1_e in action_sub_dic0.keys():
            col1_e = action_sub_dic0[col1_e]
        else:
            need_translate_ac0.append(col1_e)
        col1 = col1_b + "-" + col1_e

        if "-" in y_new_list0[num2]:
            col2_b = y_new_list0[num2].split(".")[-1].split("-")[0].rstrip()
            col2_e = y_new_list0[num2].split(".")[-1].split("-")[1].lstrip()
            if col2_b in asset_dic0.keys():
                col2_b = asset_dic0[col2_b]
            if col2_e in asset_sub_dic0.keys():
                col2_e = asset_sub_dic0[col2_e]
            else:
                need_translate_as0.append(col2_e)
            col2 = col2_b + "-" + col2_e
        else:
            col2 = y_new_list0[num2].split(".")[-1]
            if col2 in asset_dic0.keys():
                col2 = asset_dic0[col2]
        col3 = item0[1]

        table_dic0["威胁行为子类"].append(col1)
        table_dic0["受威胁资产子类"].append(col2)
        table_dic0["事件数量"].append(col3)

    if len(need_translate_ac0) != 0:
        print("The list of action: %s" % str(need_translate_ac0))
    if len(need_translate_as0) != 0:
        print("The list of asset: %s" % str(need_translate_as0))

    table_df0 = pd.DataFrame.from_dict(table_dic0)
    table_df0.to_csv(table_ops0, index=None, encoding='utf_8_sig')

    return None


# 绘制热力图
def heat_map(data0, max_value0, x_name0, y_name0, title0, label0, ops0):
    # print(title0)
    font_size0 = 18
    bias0 = 18
    height0 = str(64 * len(y_name0)) + "px"
    h = HeatMap(init_opts=opts.InitOpts(width="1300px", height=height0))
    # h = HeatMap(init_opts = opts.InitOpts(width = "1440px", height = "720px"))

    h.add_xaxis(xaxis_data=x_name0)
    h.add_yaxis(
        # 图列名称 
        series_name=label0,
        yaxis_data=y_name0,
        value=data0,
        # 图列颜色
        itemstyle_opts=opts.ItemStyleOpts(color="#9A32CD"),
        # 数字颜色
        label_opts=opts.LabelOpts(is_show=True, color="#363636",
                                  position="inside", font_size=font_size0)

    )

    h.set_global_opts(
        title_opts=opts.TitleOpts(title="",
                                  pos_bottom="0%",
                                  pos_left="center"),
        legend_opts=opts.LegendOpts(is_show=True,
                                    textstyle_opts=opts.TextStyleOpts(font_size=font_size0)),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(font_size=font_size0 + 1),
            type_="category",
            # splitline_opts = opts.SplitLineOpts(is_show=True, linestyle_opts =
            # opts.LineStyleOpts(width = 2, type_ = "solid", color="#BEBEBE")),
            splitarea_opts=opts.SplitAreaOpts(is_show=True),
        ),

        yaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(rotate=-1 * bias0, font_size=font_size0),
            type_="category",
            splitarea_opts=opts.SplitAreaOpts(is_show=True),
        ),
        visualmap_opts=opts.VisualMapOpts(
            # orient="horizontal", 
            min_=0, max_=max_value0, is_calculable=True,
            # 调节工具位置
            pos_left="90%",
            # 最小最大值映射颜色
            range_color=["#F8F8FF", "#9A32CD"]
        )
    )

    if ops0.split(".")[-1] == "html":
        h.render(ops0)
    else:
        make_snapshot(driver, h.render(), ops0)

    return None


# 绘制交叉分析的热力图
def heat_map_industry(data0, b_num0, g_ops0, type0):
    """
    data0 = data_breach
    b_num0 = 41
    label_0 = "事件占比"
    g_ops0, type0 = global_ops, ".html"
    title_0 = "全部数据泄露事件X子类和X子类热力图"
    """
    data0 = data0[(data0['action.Unknown'] == False) | (data0['action.Unknown'] == "FALSE")]
    data0 = data0[data0['victim.industry.name'] != 'Unknown']
    data0 = data0[data0['victim.industry.name'] != 'FALSE']
    data0 = data0[data0['victim.industry.name'] != '923']
    data0 = data0[data0['victim.industry.name'] != '483']
    data0 = data0[(data0["asset.assets.variety.Unknown"] == False) | (data0["asset.assets.variety.Unknown"] == "FALSE")]

    # industry
    industry_dic0 = {"Healthcare": "医疗行业", "Public": "公共部门", "Finance": "金融行业", "Information": "信息行业",
                     "Educational": "教育行业", "Retail": "零售业", "Professional": "专业服务",
                     "Other Services": "其他服务", "Unknown": "未知", "Manufacturing": "制造业",
                     "Administrative": "行政管理", "Accomodation": "住宿行业", "Transportation": "交通行业",
                     "Trade": "商业", "Entertainment": "娱乐行业", "Real Estate": "房地产", "Utilities": "公共事业",
                     "Construction": "建筑行业", "Mining": "矿业", "Management": "管理行业", "Agriculture ": "农业"}

    # pattern
    pattern_dic0 = {"Point of Sale": "销售点", "Crimeware": "犯罪软件", "Payment Card Skimmers": "支付卡读取器",
                    "Cyber-Espionage": "网络间谍", "Lost and Stolen Assets": "遗失及被盗资产",
                    "Web Applications": "网络应用程序", "Everything Else": "其他", "Privilege Misuse": "特权滥用",
                    "Miscellaneous Errors": "各种错误", "Denial of Service": "系统服务中断"}

    # action
    action_dic0 = {"Error": "错误行为", "Hacking": "黑客袭击", "Misuse": "不当使用", "Physical": "物理操作",
                   "Malware": "恶意软件", "Social": "社交策略", "Unknown": "未知因素", "Environmental": "异常环境"}

    # asset
    asset_dic0 = {"Server": "服务器", "Kiosk/Term": "自助服务终端", "Unknown": "未知", "User Dev": "用户设备",
                  "Media": "媒介", "Person": "人员", "Network": "网络", "Embedded": "嵌入式设备"}

    industry_l0 = ["victim.industry.name"]
    pattern_l0 = ["pattern"]
    action_l0 = search_action(data0, "action")
    asset_l0 = search_single_form_col(data0, "asset.variety.")

    new_dat0 = data0[industry_l0 + pattern_l0 + action_l0 + asset_l0]

    industry_unq0 = pd.DataFrame(new_dat0["victim.industry.name"].value_counts())
    industry_name0 = []
    for i0 in list(industry_unq0.index):
        if (i0 != "Unknown") and (len(industry_name0) < 10):
            industry_name0.append(i0)

    pattern_unq0 = pd.DataFrame(new_dat0["pattern"].value_counts())
    pattern_name0 = []
    for p0 in list(pattern_unq0.index):
        if (p0 != "FALSE") and (len(pattern_name0) < 10):
            pattern_name0.append(p0)

    action_name0 = []
    action_num_dic0 = {}
    for ac0 in action_l0:
        num_tmp = new_dat0[((new_dat0[ac0] == True) | (new_dat0[ac0] == "TRUE"))].shape[0]
        action_num_dic0[ac0] = num_tmp
    action_num_dic_new0 = sorted(action_num_dic0.items(), key=lambda d: d[1], reverse=True)
    for ac1 in action_num_dic_new0:
        if len(action_name0) < 6:
            action_name0.append(ac1[0])

    asset_name0 = []
    asset_num_dic0 = {}
    for as0 in asset_l0:
        num_tmp = new_dat0[((new_dat0[as0] == True) | (new_dat0[as0] == "TRUE"))].shape[0]
        asset_num_dic0[as0] = num_tmp
    asset_num_dic_new0 = sorted(asset_num_dic0.items(), key=lambda d: d[1], reverse=True)
    for as1 in asset_num_dic_new0:
        if (as1[0] != 'asset.variety.Unknown') and (len(asset_name0) < 6):
            asset_name0.append(as1[0])

            # ==============================================================
    heat_dic0 = {"pattern": [], "action": [], "asset": []}

    max_p = []
    max_ac = []
    max_as = []

    for x_it0 in range(len(industry_name0)):
        i_tmp = industry_name0[x_it0]
        for k0 in heat_dic0.keys():
            if k0 == "pattern":
                for y_it0 in range(len(pattern_name0)):
                    p_tmp = pattern_name0[y_it0]
                    num_tmp = new_dat0[((new_dat0["pattern"] == p_tmp) &
                                        (new_dat0["victim.industry.name"] == i_tmp))].shape[0]
                    heat_dic0["pattern"].append([x_it0, y_it0, num_tmp])
                    max_p.append(num_tmp)
            elif k0 == "action":
                for y_it0 in range(len(action_name0)):
                    p_tmp = action_name0[y_it0]
                    num_tmp = new_dat0[((new_dat0[p_tmp] == True) | (new_dat0[p_tmp] == "TRUE")) &
                                       (new_dat0["victim.industry.name"] == i_tmp)].shape[0]
                    heat_dic0["action"].append([x_it0, y_it0, num_tmp])
                    max_ac.append(num_tmp)
            elif k0 == "asset":
                for y_it0 in range(len(asset_name0)):
                    p_tmp = asset_name0[y_it0]
                    num_tmp = new_dat0[((new_dat0[p_tmp] == True) | (new_dat0[p_tmp] == "TRUE")) &
                                       (new_dat0["victim.industry.name"] == i_tmp)].shape[0]
                    heat_dic0["asset"].append([x_it0, y_it0, num_tmp])
                    max_as.append(num_tmp)

    max_p0 = max(max_p)
    max_ac0 = max(max_ac)
    max_as0 = max(max_as)
    max_all0 = max(max_p0, max_ac0, max_as0)

    heat_dic_cat0 = {"industry": "受威胁行业", "pattern": "威胁模式", "action": "威胁行为", "asset": "受威胁资产"}

    heat_dic_cn0 = {"industry": [], "pattern": [], "action": [], "asset": []}

    for i_c in industry_name0:
        if i_c.rstrip() in industry_dic0.keys():
            heat_dic_cn0["industry"].append(industry_dic0[i_c.rstrip()])
        else:
            heat_dic_cn0["industry"].append(i_c.rstrip())

    for p_c in pattern_name0:
        if p_c in pattern_dic0.keys():
            heat_dic_cn0["pattern"].append(pattern_dic0[p_c])
        else:
            heat_dic_cn0["pattern"].append(p_c)

    for ac_c in action_name0:
        ac_c = ac_c.split(".")[-1]
        if ac_c in action_dic0.keys():
            heat_dic_cn0["action"].append(action_dic0[ac_c])
        else:
            heat_dic_cn0["action"].append(ac_c)

    for as_c in asset_name0:
        as_c = as_c.split(".")[-1]
        if as_c in asset_dic0.keys():
            heat_dic_cn0["asset"].append(asset_dic0[as_c])
        else:
            heat_dic_cn0["asset"].append(as_c)

    label0 = "事件数量"
    heat_list_key0 = list(heat_dic0.keys())
    # heat_list_key0[k_i]
    for k_i in range(len(heat_list_key0)):
        data_list0 = heat_dic0[heat_list_key0[k_i]]
        x_l0 = heat_dic_cn0["industry"]
        y_l0 = heat_dic_cn0[heat_list_key0[k_i]]
        title0 = "图片" + str(b_num0 + k_i) + "：全部数据泄露事件" + heat_dic_cat0["industry"]
        title0 = title0 + "和" + heat_dic_cat0[heat_list_key0[k_i]] + "热力图"
        ops0 = g_ops0 + title0 + type0
        heat_map(data_list0, max_all0, x_l0, y_l0, title0, label0, ops0)

    return None


# 各行业基本信息统计
def ins_info(dat1, dat2, ins0):
    # ins0 = top9_industry_col[0]
    # ins0 = 'Public '
    # frequency
    dat1 = dat1[dat1["victim.industry.name"] == ins0]
    num1 = dat1.shape[0]
    num2 = dat2[dat2["victim.industry.name"] == ins0].shape[0]
    str0 = "安全事件共有" + str(num2) + "件，其中数据泄露事件有" + str(num1) + "件"

    dat1 = dat1[dat1["pattern"] != "FALSE"]
    dat1 = dat1[dat1["pattern"] != "622"]
    dat1 = dat1[dat1["pattern"] != "813"]
    num1 = dat1.shape[0]

    # pattern
    pattern_dic0 = {"Point of Sale": "销售点", "Crimeware": "犯罪软件", "Payment Card Skimmers": "支付卡读取器",
                    "Cyber-Espionage": "网络间谍", "Lost and Stolen Assets": "遗失及被盗资产",
                    "Web Applications": "网络应用程序", "Everything Else": "其他", "Privilege Misuse": "特权滥用",
                    "Miscellaneous Errors": "各种错误", "Denial of Service": "系统服务中断"}
    # Actor pattern

    pattern_unq0 = pd.DataFrame(dat1["pattern"].value_counts())
    pattern_value0 = list(pattern_unq0["pattern"])
    p_index0 = list(pattern_unq0.index)
    pattern_name0 = {}

    str1 = "全部数据泄露事件中："
    for p0 in range(len(p_index0)):
        if (p_index0[p0] != "FALSE") and (len(pattern_name0) < 3):
            tmp_p = 0
            if p_index0[p0] in pattern_dic0.keys():
                tmp_p = round(float(pattern_value0[p0]) / num1 * 100, 2)
                str1 = str1 + pattern_dic0[p_index0[p0]] + "占比" + str(tmp_p) + "%, "
                pattern_name0[pattern_dic0[p_index0[p0]]] = tmp_p
            else:
                pattern_name0[p_index0[p0]] = tmp_p
                str1 = str1 + p_index0[p0] + "占比" + str(tmp_p) + "%, "
    str1 = str1[:-2]

    actor_dic0 = {"External": "外部人员", "Internal": "内部人员", "Partner": "合作伙伴", "Multiple": "多方势力"}

    dat1 = dat1[dat1['Actor'] != "FALSE"]
    num1 = dat1.shape[0]

    actor_unq0 = pd.DataFrame(dat1["Actor"].value_counts())
    actor_value0 = list(actor_unq0["Actor"])
    p_index0 = list(actor_unq0.index)
    actor_name0 = {}
    str2 = "全部数据泄露事件中："
    for a0 in range(len(p_index0)):
        if (p_index0[a0] != "FALSE") and (len(actor_name0) < 3):
            if p_index0[a0] in actor_dic0.keys():
                tmp_p = round(float(actor_value0[a0]) / num1 * 100, 2)
                str2 = str2 + actor_dic0[p_index0[a0]] + "占比" + str(tmp_p) + "%, "
                actor_name0[actor_dic0[p_index0[a0]]] = tmp_p
            else:
                tmp_p = 0
                actor_name0[p_index0[a0]] = tmp_p
                str2 = str2 + p_index0[a0] + "占比" + str(tmp_p) + "%, "
    str2 = str2[:-2]

    motive_sub_dic0 = {"Convenience": "方便的权宜之计", "Espionage": "间谍活动或竞争优势", "Fear": "恐惧或胁迫",
                       "Financial": "经济或个人利益", "Fun": "有趣、好奇或自豪", "Grudge": "怨恨或个人冒犯",
                       "Ideology": "意识形态或抗议", "Secondary": "协助发动另一场攻击", "Other": "其他",
                       "Unknown": "未知"}

    sub_motive_name0 = search_motive_sub(dat1)
    # sub_motive_name0 = list(sub_dic0.keys())
    sub_motive_dat0 = motive_sub_df(sub_motive_name0, dat1)
    sub_motive_dat0 = sub_motive_dat0[(sub_motive_dat0["Unknown"] == False) | (sub_motive_dat0["Unknown"] == "FALSE")]

    sub_mo_count_dic = {}
    for m0 in sub_motive_name0:

        c0 = sub_motive_dat0[(sub_motive_dat0[m0] == True) | (sub_motive_dat0[m0] == "TRUE")].shape[0]
        # sub_mo_count_dic[m0] = round(float(c0)/num1*100, 2)
        if ('NA' not in m0) and ('Unknown' not in m0):
            sub_mo_count_dic[m0] = c0

    sub_sum_num0 = sub_motive_dat0.shape[0]

    sub_mo_count_dic = sorted(sub_mo_count_dic.items(), key=lambda d: d[1], reverse=True)

    str3 = "全部数据泄露事件中："
    for m_s in range(len(sub_mo_count_dic)):
        en_n = sub_mo_count_dic[m_s][0]
        v_n = round(float(sub_mo_count_dic[m_s][1]) / sub_sum_num0 * 100, 2)
        if (en_n != "NA") and (m_s < 3):
            if en_n in motive_sub_dic0.keys():
                str3 = str3 + motive_sub_dic0[en_n] + "占比" + str(v_n) + "%, "
            else:
                str3 = str3 + en_n + "占比" + str(v_n) + "%, "
    str3 = str3[:-2]

    data_breach_cat0 = {"Other": "其他", "Classified": "机密情报", "System": "系统信息", "Bank": "银行账户",
                        "Secrets": "商业机密", "Internal": "敏感的内部数据", "Credentials": "认证凭证",
                        "Payment": "支付卡数据", "Unknown": "未知", "Medical": "医疗记录", "Personal": "个人或身份信息"}

    del0 = "attribute.confidentiality.data.variety.Unknown"
    dat1 = dat1[(dat1[del0] == False) | (dat1[del0] == "FALSE")]

    col_name0 = list(dat1.columns)
    ac_dic0 = {}

    for item0 in col_name0:
        if "attribute.confidentiality.data.variety." in item0:
            tmp_value0 = dat1[(dat1[item0] == True) | (dat1[item0] == "TRUE")].shape[0]
            if "Unknown" not in item0:
                ac_dic0[item0] = tmp_value0

    ac_dic_new0 = sorted(ac_dic0.items(), key=lambda d: d[1], reverse=True)
    d_b_sum0 = dat1.shape[0]

    str4 = "全部数据泄露事件中："
    for it0 in range(len(ac_dic_new0)):
        dic_key0 = ac_dic_new0[it0][0].split(".")[-1]
        v_d = round(float(ac_dic_new0[it0][1]) / d_b_sum0 * 100, 2)
        if it0 < 3:
            if dic_key0 in data_breach_cat0.keys():
                str4 = str4 + data_breach_cat0[dic_key0] + "占比" + str(v_d) + "%, "
            else:
                str4 = str4 + dic_key0 + "占比" + str(v_d) + "%, "
    str4 = str4[:-2]

    return [str0, str1, str2, str3, str4]


# 分行业结果汇总
def csv_industry(dat1, dat2, table_ops0):
    """
    dat1 = data_breach
    dat2 = data_incident
    """
    industry_dic0 = {"Healthcare": "医疗行业", "Public": "公共部门", "Finance": "金融行业", "Information": "信息行业",
                     "Educational": "教育行业", "Retail": "零售业", "Professional": "专业服务",
                     "Manufacturing": "制造业", "Accomodation": "住宿行业"}

    top9_industry_col = ['Public ', 'Healthcare ', 'Finance ', 'Information ',
                         'Retail ', 'Educational ', 'Professional ',
                         'Manufacturing ', 'Accomodation ']

    csv_dic0 = {}
    for ins_0 in top9_industry_col:
        tmp_en = ins_0.rstrip()
        if tmp_en in industry_dic0.keys():
            cn_name0 = industry_dic0[tmp_en]
        else:
            cn_name0 = tmp_en
        csv_dic0[cn_name0] = ins_info(dat1, dat2, ins_0)

    table_df0 = pd.DataFrame.from_dict(csv_dic0)
    table_df0.index = ["事件次数", "威胁模式 TOP3", "威胁者", "威胁动机", "被泄露数据的类型"]
    table_df0.to_csv(table_ops0, encoding='utf_8_sig')

    return None


# 全部数据泄露事件威胁行为子类和受威胁资产子类组合Top10
def table_asset_action_all(dat_all0, global_ops0):
    # dat_all0, global_ops0 = data_breach, global_ops
    action_sub_list0 = search_action_sub(dat_all0, "action.", ".variety.")
    asset_sub_list0 = search_single_form_col(dat_all0, "asset.assets.variety.")
    table_action_asset0 = "表格1：全部数据泄露事件威胁行为子类和受威胁资产子类组合Top10"
    table_type0 = ".csv"
    deal0 = "asset.assets.variety.Unknown"
    dat_all0 = dat_all0[(dat_all0[deal0] == False) | (dat_all0[deal0] == "FALSE")]
    dat_all0 = dat_all0[(dat_all0["action.Unknown"] == False) | (dat_all0["action.Unknown"] == "FALSE")]

    csv_as_table(dat_all0, action_sub_list0, asset_sub_list0,
                 table_action_asset0, global_ops0, table_type0,
                 50, 50, 50)
    return None


# 九个行业 威胁行为子类和受威胁资产子类组合Top10
def action_asset_industry(dat_all0, b_num0, g_ops0):
    # dat_all0, b_num0, g_ops0 = data_breach, 3, global_ops
    industry_dic0 = {"Healthcare": "医疗行业", "Public": "公共部门", "Finance": "金融行业", "Information": "信息行业",
                     "Educational": "教育行业", "Retail": "零售业", "Professional": "专业服务",
                     "Manufacturing": "制造业", "Accomodation": "住宿行业"}

    deal0 = "asset.assets.variety.Unknown"
    dat_all0 = dat_all0[(dat_all0[deal0] == False) | (dat_all0[deal0] == "FALSE")]
    dat_all0 = dat_all0[(dat_all0["action.Unknown"] == False) | (dat_all0["action.Unknown"] == "FALSE")]

    top9_industry_col = ['Public ', 'Healthcare ', 'Finance ', 'Information ',
                         'Retail ', 'Educational ', 'Professional ',
                         'Manufacturing ', 'Accomodation ']

    for ins0 in range(len(top9_industry_col)):
        data0 = dat_all0[dat_all0["victim.industry.name"] == top9_industry_col[ins0]]
        if top9_industry_col[ins0].rstrip() in industry_dic0.keys():
            ins_n0 = industry_dic0[top9_industry_col[ins0].rstrip()]
        else:
            ins_n0 = top9_industry_col[ins0].rstrip()
        action_sub_list0 = search_action_sub(data0, "action.", ".variety.")
        asset_sub_list0 = search_single_form_col(data0, "asset.assets.variety.")
        table_action_asset0 = "表格" + str(b_num0 + ins0) + "：" + ins_n0
        table_action_asset0 = table_action_asset0 + "威胁行为子类和受威胁资产子类组合Top10"
        table_type0 = ".csv"
        csv_as_table(data0, action_sub_list0, asset_sub_list0,
                     table_action_asset0, g_ops0, table_type0, 0, 0, 0)

    return None


# =============================== the main function ===========================
if __name__ == '__main__':
    
    data_ops = "../data/"
    global_ops = "../picture/"

    '''
    # 原始数据集
    data_ops = "../data/vcdb_new_2019.csv"    
    data_incident = idf_read_csv(data_ops)
    
    # 初步数据处理（缺失值处理）
    new_ops = "../data/vcdb_new_2019_drop_miss.csv"
    drop_new_data = drop_miss_data(data_incident, new_ops)
    
    # 安全事件数据集
    all_incident_data_name = data_ops + "all_incident" + ".csv"
    drop_new_data.to_csv(all_incident_data_name, index = None)
       
    # 数据泄露事件数据集
    data_breach = drop_new_data[(drop_new_data["attribute.confidentiality.data_disclosure.Yes"] == True) | 
                                (drop_new_data["attribute.confidentiality.data_disclosure.Yes"] == "TRUE")]
    all_breach_data_name = data_ops + "all_breach" + ".csv"
    data_breach.to_csv(all_breach_data_name, index = None)
    '''

    incident_ops = data_ops + "all_incident.csv"
    data_incident = pd.read_csv(incident_ops, low_memory=False)
    breach_ops = data_ops + "all_breach.csv"
    data_breach = pd.read_csv(breach_ops, low_memory=False)

    data_breach_2019 = data_breach[data_breach["timeline.incident.year"] == "2019"]
    data_breach_cn = data_breach[(data_breach["victim.country.CN"] == True) |
                                 (data_breach["victim.country.CN"] == "TRUE")]

    num_label = "事件数量"
    pct_label = "事件占比"
    label_list = [num_label, pct_label]

    # file_type = ".png"
    file_type = ".html"

    label_item = label_list[1]

    actor_all_breach_title = "图片1：全部数据泄露事件各类威胁者"
    act_reversal(data_breach, actor_all_breach_title,
                 label_item, "Actor", global_ops, file_type)

    actor_2019_bre_title = "图片2：2019年数据泄露事件各类威胁者"
    act_reversal(data_breach_2019, actor_2019_bre_title,
                 label_item, "Actor", global_ops, file_type)

    actor_cn_bre_title = "图片3：中国数据泄露事件各类威胁者"
    act_reversal(data_breach_cn, actor_cn_bre_title,
                 label_item, "Actor", global_ops, file_type)

    action_all_breach_title = "图片4：全部数据泄露事件各类威胁行为"
    ac_reversal(data_breach, action_all_breach_title,
                label_item, global_ops, file_type)

    action_2019_bre_title = "图片5：2019年数据泄露事件各类威胁行为"
    ac_reversal(data_breach_2019, action_2019_bre_title,
                label_item, global_ops, file_type)

    action_cn_bre_title = "图片6：中国数据泄露事件各类威胁行为"
    ac_reversal(data_breach_cn, action_cn_bre_title,
                label_item, global_ops, file_type)

    victim_all_breach_title = "图片7：全部数据泄露事件各类受威胁行业"
    vic_reversal(data_breach, victim_all_breach_title,
                 label_item, global_ops, file_type)

    victim_2019_bre_title = "图片8：2019年数据泄露事件各类受威胁行业"
    vic_reversal(data_breach_2019, victim_2019_bre_title,
                 label_item, global_ops, file_type)

    victim_cn_bre_title = "图片9：中国数据泄露事件各类受威胁行业"
    vic_reversal(data_breach_cn, victim_cn_bre_title,
                 label_item, global_ops, file_type)

    actor_name = ["actor.Internal", "actor.External",
                  "actor.Partner", "actor.Multiple"]
    actor_all_bre_time = "图片10：全部数据泄露事件威胁者占比时序图"
    smooth_line(actor_name, data_breach, actor_all_bre_time,
                global_ops, file_type)

    data_breach_motive = motive_sub(data_breach)
    motive_name = ['Financial', 'Grudge', 'Espionage']
    motive_all_bre_time = "图片11：全部数据泄露事件威胁者动机占比时序图"
    smooth_line(motive_name, data_breach_motive, motive_all_bre_time,
                global_ops, file_type)

    data_breach_actor_var = actor_var_data("actor.", data_breach)
    actor_var_name = ['System admin', 'Organized crime',
                      'End-user', 'Unaffiliated', 'Developer',
                      'Cashier', 'Doctor or nurse', 'Other']

    actor_var_all_bre_time = "图片12：全部数据泄露事件威胁者子类占比时序图"
    smooth_line(actor_var_name, data_breach_actor_var, actor_var_all_bre_time,
                global_ops, file_type)

    action_name, action_value = diff_bar_pre_action(data_breach, "action")
    action_all_bre_diff = "图片13：全部数据泄露事件各类威胁行为占比 2014年-2019年差值"
    diff_bar(action_all_bre_diff, action_name, action_value,
             "增高/降低百分比", global_ops, file_type)

    action_subvar_name, action_subvar_value, number = action_var_data(data_breach, "action.")
    # action_subvar_name, action_subvar_value = ac_name_l_n, ac_value_l_n
    action_subvar_all_bre = "图片14：全部数据泄露事件各威胁行为子类占比" + " (样本总量：" + str(number) + "件)"
    action_subvar_all_bre_ops = global_ops + action_subvar_all_bre + file_type
    bar_reversal_pct(action_subvar_all_bre, action_subvar_name, action_subvar_value,
                     "事件占比", action_subvar_all_bre_ops)

    action_sub_top("action.", data_breach, 15, ".variety.",
                   global_ops, file_type)
    action_sub_top("action.", data_breach, 16, ".vector.",
                   global_ops, file_type)
    action_sub_top("action.", data_breach, 27, ".target.",
                   global_ops, file_type)

    pattern_pct(data_breach, "全部数据泄露事件各数据泄露模式占比",
                28, "事件占比", "pattern", global_ops, file_type)

    asset_name, asset_value = diff_bar_pre_asset(data_breach, "asset.variety.")
    asset_all_bre_diff = "图片29：全部数据泄露事件各类资产占比 2014年-2019年差值"
    diff_bar(asset_all_bre_diff, asset_name, asset_value,
             "增高/降低百分比", global_ops, file_type)

    asset_sub_top("asset.assets.variety.", data_breach, 30,
                  global_ops, file_type)

    data_variety_pct(data_breach, "全部数据泄露事件受威胁数据各类型占比",
                     31, global_ops, file_type)

    heat_map_industry(data_breach, 32, global_ops, file_type)

    # 表格1
    table_asset_action_all(data_breach, global_ops)

    table_industry_summary = global_ops + "表格2：各行业概览.csv"
    csv_industry(data_breach, data_incident, table_industry_summary)
    action_asset_industry(data_breach, 3, global_ops)
