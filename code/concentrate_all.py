# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 10:37:34 2019

@author: Zhaoke
"""
import os
import pandas as pd


def csv_file_ops(path0):
    file_ops0 = []
    all_l = os.listdir(path0)
    for i_0 in range(len(all_l)):
        file_type = os.path.splitext(all_l[i_0])[1]
        if file_type == ".csv":
            filename = os.path.splitext(all_l[i_0])[0]
            if "_end" in filename:
                file_ops0.append(path0 + all_l[i_0])

    return file_ops0


# =============================== the main function ===========================
if __name__ == '__main__':

    dir_path = "../result/"
    goal_ops = csv_file_ops(dir_path)

    final_df = pd.read_csv(goal_ops[0])

    # f = 0
    for f in range(len(goal_ops) - 1):
        tmp_df = pd.read_csv(goal_ops[f + 1])
        final_df = pd.concat([final_df, tmp_df], axis=0)

    final_ops = "../result/all_info.csv"
    final_df.to_csv(final_ops, index=None, encoding='utf_8_sig')
