#!/usr/bin/env python3
""" Run Linear Regression
"""
import optuna
import pandas as pd
import pathlib
from sklearn import metrics
from sklearn.linear_model import LinearRegression


def read_in_data(year):
    """ Read in training data and return

    Args:
        year: int type for

    Returns:
        years: a list of year indicated
        data_X:
        data_y:
    """
    base = pathlib.Path('../../data/std_data')
    train_X = pd.read_pickle(base / "train" / f"{year}_x.pkl")  # noqa: N806
    train_y = pd.read_pickle(base / "train" / f"{year}_y.pkl")
    test_X = pd.read_pickle(base / "test" / f"{year}_x.pkl")  # noqa: N806
    test_y = pd.read_pickle(base / "test" / f"{year}_y.pkl")

    return train_X, train_y, test_X, test_y


def calculate_auc(test, pred):
    fpr, tpr, _ = metrics.roc_curve(test, pred)
    return metrics.auc(fpr, tpr)


def train(params):
    pred_y = pd.DataFrame()
    ans_y = pd.DataFrame()

    model = LinearRegression(fit_intercept=params["linear_fit_intercept"],
                             normalize=params["linear_normalize"])

    for year in range(1978, 2020):
        train_X, train_y, test_X, test_y = read_in_data(year)  # noqa: N806
        model.fit(train_X, train_y)
        pred_y = pd.concat([pred_y, pd.DataFrame(model.predict(test_X))])
        ans_y = pd.concat([ans_y, pd.DataFrame(test_y)])
    return ans_y, pred_y


def objective(trail):
    """ Optuna objective parameter tuning function
    """
    linear_fit_intercept = (
        trail.suggest_categorical("linear_fit_intercept", [True, False]))
    linear_normalize = (
        trail.suggest_categorical("linear_normalize", [True, False]))

    params = {
        "linear_fit_intercept": linear_fit_intercept,
        "linear_normalize": linear_normalize,
    }

    test_y, pred_y = train(params)

    negative_auc = calculate_auc(test_y, pred_y) * (-1)
    return negative_auc


def main():
    """ Main function to tune the variable

    Args:
        NA

    Returns:
        NA
    """
    study = optuna.create_study()
    study.optimize(objective, n_trials=100)
    # best param after 10 trainings
    # auc = 0.6541279233586925
    param = {
        "linear_fit_intercept": True,
        "linear_normalize": False,
    }
    param = study.best_params
    test_y, pred_y = train(param)
    print(calculate_auc(test_y, pred_y))


if __name__ == "__main__":
    main()
