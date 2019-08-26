#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np
import json
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import softmax

from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import lightgbm as lgb
from sklearn import svm
import xgboost as xgb
import catboost
from sklearn.neural_network import MLPRegressor

from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler


# In[3]:


def load_data(y):
    path = '../data/'
    x_train_std = pd.read_pickle(path +'std_data/train/{}_x.pkl'.format(str(y))).values
    x_test_std = pd.read_pickle(path +'std_data/test/{}_x.pkl'.format(str(y))).values
    y_train = pd.read_pickle(path +'std_data/train/{}_y.pkl'.format(str(y))).values
    y_test = pd.read_pickle(path +'std_data/test/{}_y.pkl'.format(str(y))).values
    features = pd.read_pickle(path +'std_data/train/{}_x.pkl'.format(str(y))).columns
    
    with open(path +'nominate_movie_meta_data.json', 'r') as json_data:
        data = json.load(json_data)
    title = [dict["title"] for dict in data[str(y)]]

    return x_train_std, x_test_std, y_train, y_test, features, title


# In[35]:


def plot_roc_curve(fpr, tpr, auc):
    # ROC曲線をプロット
    plt.plot(fpr, tpr, label='ROC curve (area = %.2f)'%auc)
    plt.legend()
    plt.title('ROC curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.grid(True)
    plt.show()


# In[62]:


def train(y):
    
    # アンサンブルの重み  [w_lr, w_lda, w_sv, w_xgb, w_lgbm, w_cb, w_mlp]
    w = np.array([0.10583359, 0.03752913, 0.26870715, 0.09771777, 0.10549716, 0., 0.3847152 ])
        
    # データの生成
    x_train_std, x_test_std, y_train, _ , features, title = load_data(y)

    # logistic regression
    lr = LogisticRegression(class_weight="balanced", solver="liblinear",  penalty="l2", C=0.0001,  random_state=0,) # ロジスティック回帰モデルのインスタンスを作成
    lr.fit(x_train_std, y_train) # ロジスティック回帰モデルの重みを学習
    probs_lr = lr.predict_proba(x_test_std)[:,1]

    # LDA
    lda = LDA(solver="eigen", shrinkage=1).fit(x_train_std,  y_train)
    probs_lda = lda.predict_proba(x_test_std)[:,1]

    # svm
    sv = svm.SVR(kernel="sigmoid",
                                 degree=4,
                                 gamma=0.043502212815589775,
                                 coef0=0.20190829020616494,
                                 tol=0.0001,
                                 C=0.000245786293391316,
                                 epsilon=0.3056167642389302,
                                verbose=False,)
    sv.fit(x_train_std, y_train)
    probs_sv = sv.predict(x_test_std)

    # xgb
    xgboost = xgb.XGBRegressor(silent= True, 
                            random_state=0,
                           max_depth=4,
                           learning_rate=0.12765177534095626,
                           n_estimators = 46,
                           gamma=0.060805284848630535,
                           reg_lambda=4.995675788308118,
                           reg_alpha=2.1912254426545754,
                           sub_sample=0.45297631180790854,
                           scale_pos_weight=1.1672978934986058)
    xgboost.fit(x_train_std, y_train)
    probs_xgb = xgboost.predict(x_test_std)

    # lgbm
    lgbm = lgb.LGBMRegressor(
        random_state=0,
        verbosity=-1,
        bagging_seed=0,
        boost_from_average='true',
        metric='auc',
        bagging_freq=4,
        min_data_in_leaf=21,
        max_depth=13,
        learning_rate=0.08731913651405197,
        n_estimators=3394,
        subsample=0.7054763057027115,
        num_leaves=438,
        reg_lambda=0.9377125325944119,  
    )

    lgbm.fit(x_train_std, y_train)
    probs_lgbm = lgbm.predict(x_test_std)

    # catboost
    cb = catboost.CatBoostRegressor(
         random_state=0,
        iterations=258,
        depth=2,
        learning_rate=0.019083573879517587,
        random_strength=84,
        bagging_temperature=0.3233702745357832,
        od_type="Iter",
        od_wait=32, 
        logging_level='Silent')
    cb.fit(x_train_std, y_train)
    probs_cb = cb.predict(x_test_std)

    # mlp
    mlp = MLPRegressor(hidden_layer_sizes=(32,),
                       activation='relu',
                       solver='adam',
                       alpha=4.76324733221396,
                       batch_size='auto',
                       learning_rate='constant', 
                       learning_rate_init=0.0012043271455668674, 
                       power_t=0.5,
                       max_iter=1000, 
                       shuffle=True,
                       random_state=0, 
                       tol=0.0001, 
                       verbose=False, 
                       warm_start=False, 
                       momentum=0.9,
                       nesterovs_momentum=True, 
                       early_stopping=False, 
                       validation_fraction=0.1, 
                       beta_1=0.022158342014810775, 
                       beta_2= 0.7802116425099002,
                       epsilon=1e-08,
                       )
    mlp.fit(x_train_std, y_train)
    probs_mlp = mlp.predict(x_test_std)

    #アンサンブル
    all_models_probs = [probs_lr, probs_lda, probs_sv, probs_xgb, probs_lgbm, probs_cb, probs_mlp]
    
    # 各モデル結果の重み付き平均
    probs_weighted_average = np.array([0 for i in range(len(x_test_std))], dtype='float64')
    
    for probs, weight in zip(all_models_probs, w):
        probs_weighted_average += (probs * weight)
    
    probs_weighted_average = softmax(probs_weighted_average)  # ソフトマックス関数で確率に
    
    sorted_answer = sorted(list(zip(title, probs_weighted_average)), key=lambda x: -x[1])
    
    for rank, ans in enumerate(sorted_answer):
        title, prob = ans
        print(rank + 1, title, prob)

    return  probs_weighted_average



if __name__ == "__main__":
    train(2020)






