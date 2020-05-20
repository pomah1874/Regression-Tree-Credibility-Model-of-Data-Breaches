# ================
# 广义线性模型部分
# ================

# 计算描述性统计结果
library(psych)
library(stargazer)
library(MASS)
library(gamlss)

deal_path = "D:\\毕业设计\\cart_breach\\data\\"
file_list0 = dir(path = deal_path)
list_train_file0 <- grep("data_train2_.*.csv",file_list0, value = T)
merge_df = data.frame()

# 对不同数据集建模
for (file0 in list_train_file0) {
    file_name0 = paste0(deal_path, file0)
    csv_breach0 = read.csv(file = file_name0, sep=',', fileEncoding = 'UTF-8', header = T)
    col_name0 = names(csv_breach0)
    names(csv_breach0) <- gsub("\\.\\.", "_", col_name0)
    sta_rec0 = describe(csv_breach0["数据泄露量"])

    names(sta_rec0) <- c("数据名称","样本量","均值","标准差","中位数","截尾平均数","绝对中位差","最小值","最大值","值域","偏度","峰度","平均值的标准误")
    name_l0 = unlist(strsplit(file_name0, split='_'))
    cat1 = name_l0[4]
    cat2 = unlist(strsplit(name_l0[5], split='\\.'))[1]
    cat_all0 = paste(c(cat1, cat2),collapse='&')
    sta_rec0$"数据名称" = cat_all0
    rownames(sta_rec0) <- c(cat_all0)
    sta_rec_need0 = sta_rec0[ , c("数据名称", "样本量", "均值",  "标准差", "中位数", "偏度", "峰度", "最大值")]
    
    # 构建公式
    str_formula0 = paste(c(names(csv_breach0)), sep ="" ,collapse = "+")
    all_len0 = nchar(str_formula0)
    head_len0 = nchar("国家+")
    del_len0 = nchar("+数据泄露量+m")
    sub_str0 = substr(str_formula0, start = head_len0+1, stop = all_len0-del_len0)
    whole_formula0 = paste("数据泄露量 ~", sub_str0)
    # print(whole_formula0)
    
    # 导入测试集
    test_ops0 = gsub("data_train2_", "data_test2_", file_name0)
    test_df0 = read.csv(file = test_ops0, sep=',', fileEncoding = 'UTF-8', header = T)
    col_name0 = names(test_df0)
    names(test_df0) <- gsub("\\.\\.", "_", col_name0)
    num_end0 = length(names(test_df0))-2
    test_var0 = c(names(test_df0))[2:num_end0]
    test_var_df0 = test_df0[, test_var0]
    
    # Gamma
    mod_GA = gamlss(as.formula(whole_formula0), 
                    data = csv_breach0, family = GA)
    # summary(mod_GA)
    predict_GA = predict(mod_GA, newdata = test_var_df0, interval="confidence")
    mse_GA = sum((test_df0$'数据泄露量' - exp(predict_GA))^2)
    sta_rec_need0$"GA-log/(10^16)" = round(mse_GA/(10^16), 8) 
    sta_rec_need0$"GA-是否收敛" = mod_GA$converged
    
    # Exponential
    mod_EXP = gamlss(as.formula(whole_formula0), 
                     data = csv_breach0, family = EXP)
    # summary(mod_EXP)
    predict_EXP = predict(mod_EXP, newdata = test_var_df0, interval="confidence")
    mse_EXP = sum((test_df0$'数据泄露量' - exp(predict_EXP))^2)
    sta_rec_need0$"EXP-log/(10^16)" = round(mse_EXP/(10^16), 8) 
    sta_rec_need0$"EXP-是否收敛" = mod_EXP$converged
    
    # log-Normal
    mod_LOGNO = gamlss(as.formula(whole_formula0), 
                       data = csv_breach0, family = LOGNO)
    # summary(mod_LOGNO)
    predict_LOGNO = predict(mod_LOGNO, newdata = test_var_df0, interval="confidence")
    mse_LOGNO = sum((test_df0$'数据泄露量' - exp(predict_LOGNO))^2)
    sta_rec_need0$"NO-log/(10^16)" = round(mse_LOGNO/(10^16), 8)
    sta_rec_need0$"NO-是否收敛" = mod_LOGNO$converged
    
    # Pareto type 2 
    mod_PARETO2 = gamlss(as.formula(whole_formula0), 
                         data = csv_breach0, family = PARETO2)
    # summary(mod_PARETO2)
    predict_PARETO2 = predict(mod_PARETO2, newdata = test_var_df0, interval="confidence")
    mse_PARETO2 = sum((test_df0$'数据泄露量' - exp(predict_PARETO2))^2)
    sta_rec_need0$"PARETO2-log/(10^16)" = round(mse_PARETO2/(10^16), 8)
    sta_rec_need0$"PARETO2-是否收敛" = mod_PARETO2$converged
    
    # Zero adjusted Inverse Gaussian 
    mod_ZAIG = gamlss(as.formula(whole_formula0), 
                      data = csv_breach0, family = ZAIG)
    # summary(mod_ZAIG)
    predict_ZAIG = predict(mod_ZAIG, newdata = test_var_df0, interval="confidence")
    mse_ZAIG = sum((test_df0$'数据泄露量' - exp(predict_ZAIG))^2)
    sta_rec_need0$"ZAIG-log/(10^16)" = round(mse_ZAIG/(10^16), 8)
    sta_rec_need0$"ZAIG-是否收敛" = mod_ZAIG$converged
    
    # sta_rec_need0$"PO-log-AIC" = AIC(mod_po_log)
    sta_rec_need0$"GA-log-AIC" = AIC(mod_GA)
    sta_rec_need0$"EXP-log-AIC" = AIC(mod_EXP)
    sta_rec_need0$"NO-log-AIC" = AIC(mod_LOGNO)
    sta_rec_need0$"PARETO2-log-AIC" = AIC(mod_PARETO2)
    # sta_rec_need0$"PARETO2o-log-AIC" = AIC(mod_PARETO2o)
    sta_rec_need0$"ZAIG-log-AIC" = AIC(mod_ZAIG)
    
    # sta_rec_need0$"PO-log-BIC" = BIC(mod_po_log)
    sta_rec_need0$"GA-log-BIC" = BIC(mod_GA)
    sta_rec_need0$"EXP-log-BIC" = BIC(mod_EXP)
    sta_rec_need0$"NO-log-BIC" = BIC(mod_LOGNO)
    sta_rec_need0$"PARETO2-log-BIC" = BIC(mod_PARETO2)
    # sta_rec_need0$"PARETO2o-log-BIC" = BIC(mod_PARETO2o)  
    sta_rec_need0$"ZAIG-log-BIC" = BIC(mod_ZAIG)  
    
    merge_df = rbind(merge_df, sta_rec_need0) 
}

# 输出结果
save_ops0 = "D:\\毕业设计\\cart_breach\\r_result\\glm_all_info.csv"
write.csv(merge_df, save_ops0, row.names = FALSE)


# ========================
# 数据泄露量与损失金额部分
# ========================

# 交叉验证
library(caret)

csv_path = "D:\\毕业设计\\cart_breach\\picture_loss\\record_loss.csv"
csv_data0 = read.csv(file = csv_path, sep=',', fileEncoding = 'UTF-8', header = T)

set.seed(123)
five_folds <- createFolds(y = csv_data0[, 1], k = 5)

# 原始数据建模
or_rsq = vector("numeric", 5)
mod_lm_or.1 = lm(loss~record,data = csv_data0)
or1_s = summary(mod_lm_or.1)
or_rsq[1] = or1_s$r.squared
mod_lm_or.2 = lm(loss~poly(record,2),data = csv_data0)
or2_s = summary(mod_lm_or.2)
or_rsq[2] = or2_s$r.squared
mod_lm_or.3 = lm(loss~poly(record,3),data = csv_data0)
or3_s = summary(mod_lm_or.3)
or_rsq[3] = or3_s$r.squared
mod_lm_or.4 = lm(loss~poly(record,4),data = csv_data0)
or4_s = summary(mod_lm_or.4)
or_rsq[4] = or4_s$r.squared
mod_lm_or.5 = lm(loss~poly(record,5),data = csv_data0)
or5_s = summary(mod_lm_or.5)
or_rsq[5] = or5_s$r.squared
anova(mod_lm_or.1,mod_lm_or.2,mod_lm_or.3,mod_lm_or.4,mod_lm_or.5)

# 交叉验证选取最优模型
or_cv_mean_rsq = vector("numeric", 5)
five_mod_or_cv_err = vector("numeric", 5)
for(i in 1:5){
    cv.err = vector("numeric", 5)
    rsq_tmp = vector("numeric", 5)
    for(j in 1:5){
        fold_test <- csv_data0[five_folds[[j]],] # 测试集
        fold_train <- csv_data0[-five_folds[[j]],] # 训练集
        fold_mod <- lm(loss~poly(record,i), data = fold_train)
        fold_predict <- predict(fold_mod, newdata = fold_test)
        # avg_train = fold_mod$coefficients[1]
        # fold_pre_zero = max_avg(fold_predict, avg_train)
        fold_pre_zero = max_zero(fold_predict)
        cv.err[j] = mean((fold_pre_zero-fold_test$loss)^2)
        summary_mod = summary(fold_mod)
        rsq_tmp[j] = summary_mod$r.squared
    }
    five_mod_or_cv_err[i] = mean(cv.err)
    or_cv_mean_rsq[i] = mean(rsq_tmp)
}

# 绘制最优模型的观测值与拟合值散点图
loss = csv_data0$loss
record = csv_data0$record
pre_loss = predict(mod_lm_or.4)
plot(loss, pre_loss, xlab = "观测值", ylab = "拟合值", main = "四次正交多项式拟合效果", pch = "*")
abline(0,1)

# 对数数据建模
log_rsq = vector("numeric", 5)
mod_lm_log.1 = lm(log_loss~log_record,data = csv_data0)
log1_s = summary(mod_lm_log.1)
log_rsq[1] = log1_s$r.squared
mod_lm_log.2 = lm(log_loss~poly(log_record,2),data = csv_data0)
log2_s = summary(mod_lm_log.2)
log_rsq[2] = log2_s$r.squared
mod_lm_log.3 = lm(log_loss~poly(log_record,3),data = csv_data0)
log3_s = summary(mod_lm_log.3)
log_rsq[3] = log3_s$r.squared
mod_lm_log.4 = lm(log_loss~poly(log_record,4),data = csv_data0)
log4_s = summary(mod_lm_log.4)
log_rsq[4] = log4_s$r.squared
mod_lm_log.5 = lm(log_loss~poly(log_record,5),data = csv_data0)
log5_s = summary(mod_lm_log.5)
log_rsq[5] = log5_s$r.squared
anova(mod_lm_log.1,mod_lm_log.2,mod_lm_log.3,mod_lm_log.4,mod_lm_log.5)

# 交叉验证选取最优模型
log_cv_mean_rsq = vector("numeric", 5)
five_mod_log_cv_err = vector("numeric", 5)
for(i in 1:5){
    cv.err = vector("numeric", 5)
    rsq_tmp = vector("numeric", 5)
    for(j in 1:5){
        fold_test <- csv_data0[five_folds[[j]],] # 测试集
        fold_train <- csv_data0[-five_folds[[j]],] # 训练集
        fold_mod <- lm(log_loss~poly(log_record,i), data = fold_train)
        fold_predict <- predict(fold_mod, newdata = fold_test)
        cv.err[j] = mean((exp(fold_predict)-fold_test$loss)^2)
        summary_mod = summary(fold_mod)
        rsq_tmp[j] = summary_mod$r.squared
    }
    five_mod_log_cv_err[i] = mean(cv.err)
    log_cv_mean_rsq[i] = mean(rsq_tmp)
}

# 汇总信息
info_mod <- data.frame(model = c("一次多项式", "二次多项式", "三次多项式", "四次多项式", "五次多项式"),
                       original_cv = five_mod_or_cv_err,
                       log_cv = five_mod_log_cv_err,
                       original_rsq = or_rsq,
                       log_rsq = log_rsq,
                       original_cv_rsq = or_cv_mean_rsq,
                       log_cv_rsq = log_cv_mean_rsq)

# 输出结果
save_ops0 = "D:\\毕业设计\\cart_breach\\r_result\\record_loss_info.csv"
write.csv(info_mod, save_ops0, row.names = FALSE)
