#!/usr/bin/env python3
""" Run SVM
"""
import math
import numpy as np
import pandas as pd
from sklearn import svm
from sklearn import metrics
import optuna
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression


def read_in_data():
    """ Read in training data and return in np format

    Args:
        NA

    Returns:
        data:
        meta_data_X:
        meta_data_y:
    """
    data = pd.read_pickle("data.pkl")

    nomination_onehot = (
        pd.read_pickle("nomination_onehot.pkl"))
    selected_performers_onehot = (
        pd.read_pickle("selected_performers_onehot.pkl"))
    selected_directors_onehot = (
        pd.read_pickle("selected_directors_onehot.pkl"))
    selected_studio_onehot = (
        pd.read_pickle("selected_studio_onehot.pkl"))
    selected_scriptwriter_onehot = (
        pd.read_pickle("selected_scriptwriter_onehot.pkl"))

    meta_data_X = pd.concat([nomination_onehot,
                             selected_performers_onehot,
                             selected_directors_onehot,
                             selected_studio_onehot,
                             selected_scriptwriter_onehot],
                            axis=1)
    meta_data_y = data["prize"]
    meta_data_X = np.array(meta_data_X)
    meta_data_y = np.array(meta_data_y)
    return data, meta_data_X, meta_data_y


def calculate_auc(test, pred):
    fpr, tpr, _ = metrics.roc_curve(test, pred)
    return metrics.auc(fpr, tpr)


def objective(trail):
    """ Optuna objective parameter tuning function
    """
    linear_fit_intercept = trail.suggest_categorical("linear_fit_intercept", [True, False])
    linear_normalize = trail.suggest_categorical("linear_normalize", [True, False])

    params = {
        "linear_fit_intercept": linear_fit_intercept,
        "linear_normalize": linear_normalize
    }

    all_test_y, all_pred_y = run_linear_with_param(params)
    return -calculate_auc(all_test_y, all_pred_y)


def run_linear_with_param(param):
    all_test_y = []
    all_pred_y = []
    data, meta_data_X, meta_data_y = read_in_data()

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    for year in range(1978, 2020):
        train_X = []
        test_X = []
        train_y = []
        test_y = []
        titles = []
        for i in range(len(data)):
            if int(data["year"][i + 1]) != year:
                train_X.append(meta_data_X[i])
                train_y.append(meta_data_y[i])
            else:
                test_X.append(meta_data_X[i])
                test_y.append(meta_data_y[i])
                if data["prize"][i + 1] == 1:
                    titles.append("☆" + data["title"][i + 1])
                else:
                    titles.append(data["title"][i + 1])

        regression_clf = LinearRegression(
            fit_intercept=param["linear_fit_intercept"],
            normalize=param["linear_normalize"]
        )
        regression_clf.fit(train_X, train_y)
        regression_res = regression_clf.predict(test_X)
        '''
        print(year)
        for i in range(len(regression_res)):
            print(titles[i], regression_res[i])
            if list(regression_res.data).index(max(regression_res)) == i:
                if titles[i][0] == "☆":
                    true_positive += 1
                else:
                    false_positive += 1
            else:
                if titles[i][0] == "☆":
                    true_negative += 1
                else:
                    false_negative += 1
        '''
        all_pred_y += regression_res.data
        all_test_y += test_y
    return all_test_y, all_pred_y


def main():
    """ Main function to tune the variable

    Args:
        NA

    Returns:
        NA
    """
    study = optuna.create_study()
    study.optimize(objective, n_trials=10)
    # best param after 10 trainings
    # best auc 0.6424344885883347
    param = {
        "linear_fit_intercept": True,
        "linear_normalize": True
    }
    param = study.best_params
    test_y, pred_y = run_linear_with_param(param)
    print(calculate_auc(test_y, pred_y))


if __name__ == "__main__":
    main()
