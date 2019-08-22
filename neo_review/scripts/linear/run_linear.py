#!/usr/bin/env python3
""" Run Linear Regression
"""
import math
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
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
    data = pd.read_pickle("unificated_data_set.pkl")
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

    model = LinearRegression(
        fit_intercept=params["linear_fit_intercept"],
        normalize=params["linear_normalize"],
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
    linear_fit_intercept = trail.suggest_categorical("linear_fit_intercept", [True, False])
    linear_normalize = trail.suggest_categorical("linear_normalize", [True, False])
    params = {
        "linear_fit_intercept": linear_fit_intercept,
        "linear_normalize": linear_normalize,
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
    study.optimize(objective, n_trials=10)
    # best param after 10 trainings
    # auc = 0.6699774584389969
    param = {
        "linear_fit_intercept": True,
        "linear_normalize": False,
    }
    param = study.best_params
    test_y, pred_y = train(param)
    print(calculate_auc(test_y, pred_y))


if __name__ == "__main__":
    main()
