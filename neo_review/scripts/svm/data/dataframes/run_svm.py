#!/usr/bin/env python3
""" Run SVM
"""
import math
import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn import metrics
import optuna


def read_in_data():
    """ Read in training data and return

    Args:
        NA

    Returns:
        years: a list of year indicated
        data_X:
        data_y:
    """
    data = pd.read_pickle("pos_val_df.pkl")
    # data = pd.read_pickle("unificated_data_set.pkl")
    years = data["year"]
    data_y = data["prize"]
    data_X = data.drop(["year", "prize"], axis=1)
    return years, data_X, data_y

def calculate_auc(test, pred):
    fpr, tpr, _ = metrics.roc_curve(test, pred)
    return metrics.auc(fpr, tpr)

def train(params):
    years, data_X, data_y = read_in_data()
    pred_y = pd.DataFrame()
    ans_y = pd.DataFrame()

    model = SVR(
        kernel=params["svm_kernel"],
        degree=params["svm_degree"],
        gamma=params["svm_gamma"],
        coef0=params["svm_coef0"],
        tol=params["svm_tol"],
        C=params["svm_c"],
        epsilon=params["svm_epsilon"],
        max_iter=10000
    )

    for year in range(1978, 2020):
        train_X = data_X[years != year]
        train_y = data_y[years != year]
        test_X = data_X[years == year] 
        test_y = data_y[years == year]

        model.fit(train_X, train_y)
        pred_y = pd.concat([pred_y, pd.DataFrame(model.predict(test_X))])
        ans_y = pd.concat([ans_y, pd.DataFrame(test_y)])
    
    return ans_y, pred_y

def objective(trail):
    """ Optuna objective parameter tuning function
    """
    svm_kernel = trail.suggest_categorical("svm_kernel", ["linear", "rbf", "poly", "sigmoid"])
    svm_degree = trail.suggest_int("svm_degree", 3, 10)
    svm_gamma = trail.suggest_uniform("svm_gamma", 0.01, 1)
    svm_coef0 = trail.suggest_uniform("svm_coef0", -1, 1)
    svm_tol = trail.suggest_categorical("svm_tol", [math.pow(10, i) for i in range(-3, 0)])
    svm_c = trail.suggest_categorical("svm_c", [math.pow(10, i) for i in range(-5, 5)])
    svm_epsilon = trail.suggest_uniform("svm_epsilon", 0.1, 1)

    params = {
        "svm_kernel": svm_kernel,
        "svm_degree": svm_degree,
        "svm_gamma": svm_gamma,
        "svm_coef0": svm_coef0,
        "svm_tol": svm_tol,
        "svm_c": svm_c,
        "svm_epsilon": svm_epsilon
    }

    test_y, pred_y = train(params)
    return -calculate_auc(test_y, pred_y)


def main():
    """ Main function to tune the variable

    Args:
        NA

    Returns:
        NA
    """
    study = optuna.create_study()
    study.optimize(objective, n_trials=1000)
    # best param after 1000 trainings
    # auc 0.7683150183150182
    param = {
        'svm_kernel': 'sigmoid', 
        'svm_degree': 5, 
        'svm_gamma': 0.30268493071866936, 
        'svm_coef0': 0.38707331192266087, 
        'svm_tol': 0.1, 
        'svm_c': 0.01, 
        'svm_epsilon': 0.3681951403297184
    }
    param = study.best_params
    test_y, pred_y = train(param)
    print(calculate_auc(test_y, pred_y))

if __name__ == "__main__":
    main()
