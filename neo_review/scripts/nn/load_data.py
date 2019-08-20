import chainer
import numpy as np
import pandas as pd
from chainer.datasets import split_dataset, split_dataset_random


class LoadData:
    def __init__(self):
        self.data_pass = '../../data/dataframes/'
        data = pd.read_pickle(self.data_pass + 'data.pkl')
        nomination_onehot = pd.read_pickle(self.data_pass + 'nomination_onehot.pkl')
        selected_performers_onehot = pd.read_pickle(self.data_pass + 'selected_performers_onehot.pkl')
        selected_directors_onehot = pd.read_pickle(self.data_pass + 'selected_directors_onehot.pkl')
        selected_studio_onehot = pd.read_pickle(self.data_pass + 'selected_studio_onehot.pkl')
        selected_scriptwriter_onehot = pd.read_pickle(self.data_pass + 'selected_scriptwriter_onehot.pkl')
        review_dataframe = pd.read_pickle(self.data_pass + 'review_dataframe.pkl')
        self.df = pd.concat(
            [nomination_onehot, selected_performers_onehot, selected_directors_onehot, selected_studio_onehot,
             selected_scriptwriter_onehot, data["screen_time"]],
            axis=1).astype(np.float32)
        self.result = data["prize"].astype(np.float32)

    def __call__(self, *args, **kwargs):
        pass

    def split_data(self, test_mode=False):
        data = self.df.values
        if test_mode:
            train_test = chainer.datasets.DictDataset(x=data, y=self.result.values)
            train, test = split_dataset(train_test, len(train_test))
        else:
            train, test = self.split_train_test(data)
        return train, test

    def split_train_test(self, data, test_ratio=0.01):
        count = len(data)
        train_num = count - int(count * test_ratio)
        train_test = chainer.datasets.DictDataset(x=data, y=self.result.values)
        train, test = split_dataset_random(train_test, train_num, seed=0)
        return train, test
