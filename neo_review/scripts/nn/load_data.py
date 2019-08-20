import chainer
import numpy as np
import pandas as pd
from sklearn import preprocessing


class LoadData:
    def __init__(self):  # HACK: refactor init
        self.data_pass = '../../data/dataframes/'
        self.other_data = pd.read_pickle(self.data_pass + 'data.pkl')
        nomination_onehot = pd.read_pickle(self.data_pass + 'nomination_onehot.pkl')
        selected_performers_onehot = pd.read_pickle(self.data_pass + 'selected_performers_onehot.pkl')
        selected_directors_onehot = pd.read_pickle(self.data_pass + 'selected_directors_onehot.pkl')
        selected_studio_onehot = pd.read_pickle(self.data_pass + 'selected_studio_onehot.pkl')
        selected_scriptwriter_onehot = pd.read_pickle(self.data_pass + 'selected_scriptwriter_onehot.pkl')
        review_dataframe = pd.read_pickle(self.data_pass + 'review_dataframe.pkl')
        self.x = pd.concat(
            [
                nomination_onehot,
                selected_performers_onehot,
                selected_directors_onehot,
                selected_studio_onehot,
                selected_scriptwriter_onehot,
                self.other_data['screen_time'],
                self.other_data['year'],
            ],
            axis=1).astype(np.float32)
        self.gen = self.cv_generator(self.other_data, self.x)

    def __call__(self, *args, **kwargs):
        pass

    def cv_generator(self, data, df):
        for year in range(1978, 2020):
            train = chainer.datasets.DictDataset(x=df[df["year"] != year].drop(["year"], axis=1)
                                                 .values.astype(np.float32),
                                                 y=data[data["year"] != year]["prize"].values.astype(np.float32))
            test = chainer.datasets.DictDataset(x=df[df["year"] == year].drop(["year"], axis=1)
                                                .values.astype(np.float32),
                                                y=data[data["year"] == year]["prize"].values.astype(np.float32))
            title = self.other_data[self.other_data["year"] == year]["title"].values
            '''
            std_x_train, std_x_test = self.standarize(train_x, test_x)
            yield (std_x_train, train_y, std_x_test, test_y)
            '''
            yield train, test, title

    def standarize(self, x_train, x_test):
        scaler = preprocessing.StandardScaler()
        std_x_train = scaler.fit_transform(x_train)
        std_x_test = scaler.transform(x_test)
        return std_x_train, std_x_test
