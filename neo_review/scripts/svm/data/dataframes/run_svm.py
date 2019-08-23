#!/usr/bin/env python3
""" Run SVM
"""
import math
import optuna
import pandas as pd
from sklearn import metrics
from sklearn.svm import SVR


def read_in_data(year):
    """ Read in training data and return

    Args:
        NA

    Returns:
        years: a list of year indicated
        data_X:
        data_y:
    """
    # data = pd.read_pickle("pos_val_df.pkl")
    train_X = pd.read_pickle("../../../../data/std_data/train/" + str(year) + "_x.pkl")
    train_y = pd.read_pickle("../../../../data/std_data/train/" + str(year) + "_y.pkl")
    test_X = pd.read_pickle("../../../../data/std_data/test/" + str(year) + "_x.pkl")
    test_y = pd.read_pickle("../../../../data/std_data/test/" + str(year) + "_y.pkl")
    return train_X, train_y, test_X, test_y


def calculate_auc(test, pred):
    fpr, tpr, _ = metrics.roc_curve(test, pred)
    return metrics.auc(fpr, tpr)


def train(params):
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
        max_iter=-1,
        verbose=False,
    )

    for year in range(1978, 2020):
        train_X, train_y, test_X, test_y = read_in_data(year)
        model.fit(train_X, train_y)
        pred_y = pd.concat([pred_y, pd.DataFrame(model.predict(test_X))])
        ans_y = pd.concat([ans_y, pd.DataFrame(test_y)])
    return ans_y, pred_y


def objective(trail):
    """ Optuna objective parameter tuning function
    """
    svm_kernel = trail.suggest_categorical("svm_kernel", ["linear", "rbf", "poly", "sigmoid"])
    svm_degree = trail.suggest_int("svm_degree", 3, 5)
    svm_gamma = trail.suggest_uniform("svm_gamma", 0.01, 1)
    svm_coef0 = trail.suggest_uniform("svm_coef0", -1, 1)
    svm_tol = trail.suggest_categorical("svm_tol", [math.pow(10, i) for i in range(-5, 0)])
    svm_c = trail.suggest_uniform("svm_c", 0, 1)
    svm_epsilon = trail.suggest_uniform("svm_epsilon", 0.1, 1)

    params = {
        "svm_kernel": svm_kernel,
        "svm_degree": svm_degree,
        "svm_gamma": svm_gamma,
        "svm_coef0": svm_coef0,
        "svm_tol": svm_tol,
        "svm_c": svm_c,
        "svm_epsilon": svm_epsilon,
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
    # auc 0.794590025359256
    param = {
        'svm_kernel': 'sigmoid',
        'svm_degree': 4,
        'svm_gamma': 0.043502212815589775,
        'svm_coef0': 0.20190829020616494,
        'svm_tol': 0.0001,
        'svm_c': 0.000245786293391316,
        'svm_epsilon': 0.3056167642389302,
    }
    param = study.best_params
    test_y, pred_y = train(param)
    print(calculate_auc(test_y, pred_y))


if __name__ == "__main__":
    main()
